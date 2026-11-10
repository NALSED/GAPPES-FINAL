// Tableau de bord (document 18) : la seule page qui regarde l'ensemble du programme. Deux moitiés : la
// recherche en cours (ou la dernière terminée) en haut, l'état du système en bas. Rien ne se rafraîchit tout
// seul sauf pendant qu'une recherche tourne (§4) : pas de WebSocket ni d'EventSource, aucune des deux n'existe
// ailleurs dans /suite.
import { api, apiAssistant } from "./api.js";
import { h, icone } from "./dom.js";
import { agir, app, sourceParId } from "./etat.js";
import { ETATS_RECHERCHE, VERBES, aPluriel, fmtDate, fmtNombre, SEUIL_QUOTA } from "./mots.js";
import { bouton, boutonIcone, carteRepliable, etiquetteRole, quotaVue } from "./ui.js";

const T = {
  recherche: null, // la recherche regardée (en cours, sinon en attente, sinon la dernière terminée)
  autres: [], // les autres recherches en cours ou en attente, en une ligne cliquable (§2.1)
  programmes: null, journal: null, // chargés une fois par arrivée sur la page (§4, moitié basse non rafraîchie)
  repliees: lireRepliees(), // mémorisées comme les blocs de Réglages
  intervalle: null,
};

/** Lu au chargement du module : une valeur illisible ou un stockage bloqué feraient tomber toute l'application. */
function lireRepliees() {
  try { return new Set(JSON.parse(localStorage.getItem("tableau-cartes-repliees") || "[]")); } catch { return new Set(); }
}

function memoriserRepli(id, repliee) {
  repliee ? T.repliees.add(id) : T.repliees.delete(id);
  try { localStorage.setItem("tableau-cartes-repliees", JSON.stringify([...T.repliees])); } catch { /* navigateur privé : la page marche quand même */ }
}

function pastilleRecherche(etat) {
  const e = ETATS_RECHERCHE[etat] || { classe: "off", mot: etat };
  return h("span", { class: "etat" }, h("span", { class: `pastille ${e.classe}`, "aria-hidden": "true" }), h("span", {}, e.mot));
}

function duree(debut, fin, enCours) {
  if (!debut) return "";
  const ms = (fin ? new Date(fin) : new Date()) - new Date(debut);
  const min = Math.round(ms / 60000);
  const texte = min < 1 ? "moins d'1 min" : aPluriel(min, "minute", "minutes");
  return enCours ? `depuis ${texte}` : `a duré ${texte}`;
}

async function chargerRecherche() {
  const toutes = await api.recherches();
  const actives = toutes.filter((r) => r.etat === "en_cours");
  const attente = toutes.filter((r) => r.etat === "en_attente");
  const courante = actives[0] || attente[0] || toutes.find((r) => r.etat !== "en_attente" && r.etat !== "en_cours") || null;
  T.recherche = courante;
  T.autres = [...actives, ...attente].filter((r) => r.id !== courante?.id);
}

async function chargerEtatSysteme() {
  const [reglages, programmes, journal] = await Promise.all([apiAssistant.reglages(), api.programmes(), api.journal()]);
  T.reglages = reglages;
  T.programmes = programmes;
  T.journal = journal;
}

function arreterPoll() {
  if (T.intervalle) { clearInterval(T.intervalle); T.intervalle = null; }
}

function demarrerPollSiBesoin() {
  arreterPoll();
  if (!T.recherche || !["en_cours", "en_attente"].includes(T.recherche.etat)) return;
  T.intervalle = setInterval(async () => {
    if (document.visibilityState !== "visible") return; // §4 : s'arrête dès que l'onglet n'est plus affiché
    try {
      T.recherche = await api.recherche(T.recherche.id);
    } catch {
      return; // un essai raté n'arrête pas le sondage : le suivant retentera
    }
    if (!["en_cours", "en_attente"].includes(T.recherche.etat)) arreterPoll();
    app.rendre();
  }, 2000);
}

function sujetPhrase(sujet) {
  const s = sujet || {};
  return [s.quoi, (s.inclure || []).join(", "), s.lieu, s.pays].filter(Boolean).join(" · ") || "(sans sujet)";
}

function enTeteRecherche(r) {
  const av = r.avancement || {};
  const enCours = r.etat === "en_cours";
  return h(
    "div", { class: "champ" },
    h("div", { class: "deux-col" },
      h("div", {}, h("span", { class: "fort" }, sujetPhrase(r.sujet)), h("p", { class: "douce" }, av.message || r.message || "")),
      h("div", { class: "droite" }, pastilleRecherche(r.etat))),
    h("p", { class: "legende" }, `${r.qui} · ${duree(r.debut, r.fin, enCours)}`),
    T.autres.length > 0 && h("button", { type: "button", class: "lien-discret", onclick: () => { T.recherche = T.autres[0]; demarrerPollSiBesoin(); app.rendre(); } },
      aPluriel(T.autres.length, "autre recherche en cours ou en attente", "autres recherches en cours ou en attente")),
    enCours && bouton({ libelle: av.en_pause ? VERBES.reprendre : VERBES.pause, icon: "interrupteur", petit: true, onclick: () => bascPause(r, !!av.en_pause) }),
    enCours && bouton({ libelle: VERBES.arreter, icon: "interrupteur", petit: true, variante: "danger", onclick: () => arreter(r) }),
    r.etat === "terminee" && bouton({ libelle: VERBES.reutiliser, icon: "reutiliser", petit: true, onclick: () => { location.hash = "#/recherche/sauvegardees"; } }),
  );
}

async function arreter(r) {
  const ok = await agir(() => api.arreterRecherche(r.id), { succes: "Arrêt demandé : ce qui est déjà collecté est gardé.", rechargerApres: false });
  if (ok) { T.recherche = await api.recherche(r.id); app.rendre(); }
}

// 908, étape 6, point 1 (retour du 08/11/2026) : portage de la pause/reprise d'une recherche en cours, sur
// les routes déjà existantes (`/api/recherches/{id}/pause` et `/reprise`, partagées avec l'ancienne page).
async function bascPause(r, enPause) {
  const ok = await agir(() => (enPause ? apiAssistant.repriseRecherche(r.id) : apiAssistant.pauseRecherche(r.id)), { rechargerApres: false });
  if (ok) { T.recherche = await api.recherche(r.id); app.rendre(); }
}

function sectionTuiles(r) {
  const tuiles = (r.avancement?.plan?.tuiles) || {};
  const ids = Object.keys(tuiles);
  if (!ids.length) return null; // recherche simple, sans plan de travail : §2.3 ne s'affiche pas
  return h(
    "div", { class: "champ" }, h("span", { class: "titre-champ" }, "Le plan en train de tourner"),
    h("div", { class: "options-grille" }, ids.map((id) => {
      const t = tuiles[id];
      const active = r.avancement?.prise && t.nom && r.avancement.prise === t.nom; // approximatif : le pont ne nomme pas encore la tuile active elle-même
      return h("div", { class: `tuile-compteur ${active ? "active" : ""}`.trim() },
        h("span", {}, t.nom),
        h("span", { class: "chiffres" }, `${fmtNombre(t.entrees)} entrés → ${fmtNombre(t.sorties)} sortis`));
    })),
  );
}

function sectionSources(r) {
  const prises = (r.avancement?.prises) || {};
  const ids = Object.keys(prises);
  if (!ids.length) return null;
  const couts = r.couts || {};
  return h(
    "div", { class: "champ" }, h("span", { class: "titre-champ" }, "Les sources au travail"),
    h("div", { class: "carte-corps liste" }, ids.map((pid) => {
      const p = prises[pid];
      const source = sourceParId(pid);
      const active = r.avancement?.prise === pid;
      return h("div", { class: `ligne ${active ? "active" : ""}`.trim() },
        h("span", { class: "c-nom" }, source ? h("span", { class: "fort" }, source.nom) : pid, source && etiquetteRole(source.role)),
        h("span", {}, `${fmtNombre(p.faits)} / ${fmtNombre(p.prevus)} appels`),
        h("span", {}, p.fini ? `${fmtNombre(p.trouves)} trouvés` : "en cours"),
        source && couts[source.id] && h("span", { class: "legende" }, `${(couts[source.id].dollars ?? 0).toFixed(4)} crédits`));
    })),
  );
}

function sectionResultats(r) {
  const av = r.avancement || {};
  if (!av.noms && av.noms !== 0) return null;
  return h(
    "div", { class: "champ" }, h("span", { class: "titre-champ" }, "Ce que la recherche a trouvé"),
    h("p", { class: "chiffres fort" }, `${fmtNombre(av.noms)} ${av.noms > 1 ? "noms trouvés" : "nom trouvé"}`),
  );
}

function sectionCout(r) {
  const total = Object.values(r.couts || {}).reduce((s, c) => s + (c.dollars || 0), 0);
  if (!total) return null;
  return h("p", { class: "legende" }, `Coût de cette recherche jusqu'ici : ${total.toFixed(4)} crédits`);
}

function sectionAlertes(r, reglages) {
  const alertes = [];
  const b = reglages?.budget;
  if (b && b.plafond_mensuel_usd > 0) {
    const pct = Math.round((b.depense_du_mois_usd / b.plafond_mensuel_usd) * 100);
    if (pct >= SEUIL_QUOTA) alertes.push(`Le budget du mois est à ${pct} %.`);
  }
  for (const s of (app.data.sources || [])) {
    if (s.pct != null && s.pct >= SEUIL_QUOTA) alertes.push(`${s.nom} : quota à ${s.pct} % ce mois.`);
  }
  for (const [id, raison] of Object.entries((r.avancement?.sources_en_pause || []).reduce((o, x) => ({ ...o, [x.source || x]: x.raison || "plusieurs erreurs de suite" }), {}))) {
    const nom = sourceParId(id)?.nom || id;
    alertes.push(`${nom} est en pause : ${raison}.`);
  }
  if (r.avancement?.limitee_aux_gratuites) alertes.push("Plafond du mois atteint : seules les sources gratuites sont interrogées.");
  // 2.3 (retour du 08/11/2026) : l'effet « alerte » du Compteur budget (seuil « À partir de … %», action « Prévenir »)
  // n'avait aucun chemin jusqu'ici — calculé par l'exécuteur (executeur_grappes.verifier_alerte_budget), affiché ici.
  if (r.avancement?.alerte_budget) alertes.push(r.avancement.alerte_budget);
  // 909, point 1.2.a : une alerte de vérification (ex. liste de sanctions) n'apparaissait que dans la fiche
  // du candidat en Tri — visible ici aussi, sans attendre qu'une personne l'ouvre.
  (r.avancement?.alertes_verification || []).forEach((a) => alertes.push(a));
  if (!alertes.length) return null;
  return h("div", { class: "champ" }, alertes.map((texte) => h("div", { class: "alerte-ligne" }, icone("attention", 20), h("span", {}, texte))));
}

function moitieHaute() {
  if (!T.recherche) return h("p", { class: "vide" }, "Aucune recherche à montrer pour l'instant.");
  const r = T.recherche;
  return h("div", { class: "tableau-moitie" }, enTeteRecherche(r), sectionAlertes(r, T.reglages), sectionTuiles(r), sectionSources(r), sectionResultats(r), sectionCout(r));
}

function carteBudget() {
  const b = T.reglages?.budget;
  if (!b) return null;
  const pct = b.plafond_mensuel_usd > 0 ? Math.round((b.depense_du_mois_usd / b.plafond_mensuel_usd) * 100) : 0;
  const chaud = pct >= SEUIL_QUOTA;
  return carteRepliable({
    titre: "Budget du mois", compte: `${b.depense_du_mois_usd.toFixed(2)} / ${b.plafond_mensuel_usd.toFixed(2)} crédits`,
    ouverte: !T.repliees.has("budget"), onbascule: () => { memoriserRepli("budget", !T.repliees.has("budget")); app.rendre(); },
    corps: h("div", { class: "carte-corps" },
      h("div", { class: `quota ${chaud ? "chaud" : ""}`.trim() },
        h("span", { class: "quota-texte" }, `${b.depense_du_mois_usd.toFixed(2)} / ${b.plafond_mensuel_usd.toFixed(2)} crédits ce mois (${pct} %)`),
        h("span", { class: "jauge", role: "img", "aria-label": `${pct} % du budget` }, h("span", { style: { width: `${Math.min(100, pct)}%` } }))),
      h("p", { class: "legende" }, "Le détail par source se lit dans la recherche en cours (coût), pas répété ici.")),
  });
}

function carteSources() {
  const sources = (app.data.sources || []).filter((s) => !s.retiree);
  if (!sources.length) return null;
  const compte = { ok: 0, warn: 0, off: 0 };
  for (const s of sources) compte[s.etat === "ok" ? "ok" : s.etat === "off" ? "off" : "warn"] += 1;
  const enPause = sources.filter((s) => s.en_pause);
  return carteRepliable({
    titre: "Sources", compte: `${aPluriel(sources.length, "source", "sources")} · ${compte.ok} opérationnelle${compte.ok > 1 ? "s" : ""}`,
    ouverte: !T.repliees.has("sources"), onbascule: () => { memoriserRepli("sources", !T.repliees.has("sources")); app.rendre(); },
    corps: h("div", { class: "carte-corps liste" },
      h("p", { class: "legende" }, `${compte.ok} opérationnelle${compte.ok > 1 ? "s" : ""} · ${compte.warn} à vérifier · ${compte.off} éteinte${compte.off > 1 ? "s" : ""}`),
      enPause.length > 0 && enPause.map((s) => h("div", { class: "ligne" },
        h("span", { class: "fort" }, s.nom), h("span", { class: "legende" }, s.en_pause.raison),
        boutonIcone({ icon: "interrupteur", etiquette: `${VERBES.reprendre} ${s.nom}`, onclick: () => agir(() => api.post(`/sources/${s.id}/reprendre`), { succes: `« ${s.nom} » reprend le travail.` }) }))),
      sources.filter((s) => s.pct != null).map((s) => h("div", { class: "ligne" }, h("span", {}, s.nom), quotaVue({ ...s, quota: s.quota, pct: s.pct, etat: s.etat })))),
  });
}

function cartesProgrammes() {
  const p = T.programmes || [];
  if (!p.length) return null; // absente si rien n'est programmé
  return carteRepliable({
    titre: "Recherches programmées", compte: String(p.length),
    ouverte: !T.repliees.has("programmes"), onbascule: () => { memoriserRepli("programmes", !T.repliees.has("programmes")); app.rendre(); },
    corps: h("div", { class: "carte-corps liste" }, p.map((x) => h("div", { class: "ligne" },
      h("span", { class: "fort" }, x.libelle), h("span", { class: "legende" }, x.prochaine ? fmtDate(x.prochaine) : "en pause")))),
  });
}

const PHRASE_EVENEMENT = {
  creation: "Recherche créée", debut: "Recherche démarrée", fin: "Recherche terminée", pause: "Recherche mise en pause",
  arret_demande: "Arrêt demandé", interrompue_au_redemarrage: "Interrompue par un redémarrage du programme",
  export: "Résultats exportés", decision_groupee: "Décisions prises en lot", decision_annulee: "Décision annulée",
  noms_separes: "Fiches séparées", rapprochements_proposes: "Rapprochements proposés", source_ajoutee: "Source ajoutée",
  prise_ajoutee: "Source ajoutée à une recherche", programme_cree: "Recherche programmée", programme_repris: "Recherche programmée reprise",
};

function phraseJournal(e) {
  if (e.evenement === "tuile_passee") return `${e.detail.nom} : ${fmtNombre(e.detail.traversees)} fiches traversées, ${fmtNombre(e.detail.modifiees)} modifiées`;
  if (e.evenement === "plan_ia_appels") {
    const d = e.detail;
    let base = `Assistant IA : ${aPluriel(d.n || 0, "appel", "appels")}, ${fmtNombre(d.tokens || 0)} jetons`;
    if (d.echecs) base += `, ${aPluriel(d.echecs, "échec", "échecs")}`;
    if (d.plafonnees) base += `, ${fmtNombre(d.plafonnees)} non traitée(s) (plafond)`;
    return base;
  }
  return PHRASE_EVENEMENT[e.evenement] || e.evenement;
}

function carteJournal() {
  const j = T.journal || [];
  return carteRepliable({
    titre: "Journal", compte: String(j.length),
    ouverte: !T.repliees.has("journal"), onbascule: () => { memoriserRepli("journal", !T.repliees.has("journal")); app.rendre(); },
    corps: h("div", { class: "carte-corps liste" },
      j.length ? j.map((e) => h("div", { class: "ligne" }, h("span", { class: "legende" }, fmtDate(e.le)), h("span", {}, e.qui), h("span", {}, phraseJournal(e))))
        : h("p", { class: "legende" }, "Rien pour l'instant.")),
  });
}

function moitieBasse() {
  return h("div", { class: "tableau-moitie" }, carteBudget(), carteSources(), cartesProgrammes(), carteJournal());
}

export function pageTableau() {
  return [h("div", { class: "page-tete" }, h("div", { class: "page-titre" }, h("h1", {}, "Tableau de bord"))),
    h("div", { class: "deux-col" }, moitieHaute(), moitieBasse())];
}

export async function chargerTableau() {
  app.rendre(); // affiche tout de suite la coquille de la page (onglet actif, titre) pendant que les données arrivent
  await Promise.all([chargerRecherche(), chargerEtatSysteme()]);
  demarrerPollSiBesoin();
  app.rendre();
}

export function quitterTableau() {
  arreterPoll();
}
