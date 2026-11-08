// Rendu des options d'un outil par genre de modèle livré (3.8.0X) : remplace le champ texte générique par un
// vrai composant quand le genre en a un. Partagé entre plan.js (tuile posée sur le plan de travail) et
// reglages.js (fiche de réglage par défaut de l'outil, dans Réglages › Outils) : une seule source de vérité
// pour les vocabulaires fermés, pour que les deux écrans ne divergent plus jamais (spécification 905 § 1).
//
// `n` est n'importe quel objet exposant `.opts` (liste [libellé, valeur]) ; `guarder` est appelé après chaque
// mutation pour que l'appelant persiste à sa façon (sauvegarde immédiate du plan, ou rien : la fiche outil ne
// persiste qu'au clic sur Enregistrer).
import { api, Refus } from "./api.js";
import { h } from "./dom.js";
import { EFFORTS_IA, VERBES } from "./mots.js";
import { bouton, boutonIcone, caseSource, champ, groupePuces, puce } from "./ui.js";

export const genreDeOutil = (o) => (o && o.nature !== "script" ? o.modele || o.id : null);

let FORMATS_CACHE = null;
async function chargerFormats() {
  if (!FORMATS_CACHE) FORMATS_CACHE = await api.formats();
  return FORMATS_CACHE;
}
const optLabel = (n, lib) => (n.opts.find((p) => p[0] === lib) || [])[1] || "";
function optDefinir(n, lib, valeur) {
  const o = n.opts.find((p) => p[0] === lib);
  if (o) o[1] = valeur;
  else n.opts.push([lib, valeur]);
}
function optRetirer(n, lib) {
  n.opts = n.opts.filter((p) => p[0] !== lib);
}

/** 3.8.01 : menu fermé dynamique (pilote.formats.vue, pas CSV/JSON en dur) + une section par format choisi,
 *  construite depuis ce que CE format déclare de lui-même (contenus, séparateur pour CSV, champs « besoin »). */
function rendreOptionsFormat(n, refresh, guarder) {
  if (!FORMATS_CACHE) {
    chargerFormats().then(refresh);
    return h("p", { class: "legende" }, "Les formats arrivent…");
  }
  const choisis = optLabel(n, "Format de sortie").toLowerCase().split(/\s+/).filter(Boolean);
  const bascule = (fid) => {
    const s = new Set(choisis);
    if (s.has(fid)) {
      s.delete(fid);
      const f = FORMATS_CACHE.find((x) => x.id === fid);
      optRetirer(n, `${f.nom} : contenu`);
      if (fid === "csv") optRetirer(n, "Séparateur");
      (f.besoin || []).forEach((b) => optRetirer(n, `${f.nom} : ${b}`));
    } else s.add(fid);
    optDefinir(n, "Format de sortie", [...s].join(" ").toUpperCase());
    guarder();
    refresh();
  };
  const sections = FORMATS_CACHE.filter((f) => choisis.includes(f.id)).map((f) => {
    const champs = [];
    if (f.contenus.length > 1) {
      const lib = `${f.nom} : contenu`;
      champs.push(h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Contenu"),
        groupePuces(f.contenus.map((c) => [c, c]), optLabel(n, lib) || f.contenus_defaut[0], (v) => { optDefinir(n, lib, v); guarder(); refresh(); })));
    }
    if (f.id === "csv") {
      const lib = "Séparateur";
      champs.push(h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Séparateur"),
        groupePuces([[";", ";"], [",", ","]], optLabel(n, lib) || ";", (v) => { optDefinir(n, lib, v); guarder(); refresh(); })));
    }
    (f.besoin || []).forEach((champBesoin) => {
      const lib = `${f.nom} : ${champBesoin}`;
      const c = champ({ libelle: `${f.nom} — ${champBesoin}`, valeur: optLabel(n, lib), placeholder: champBesoin === "url" ? "https://…" : "" });
      c.saisie.addEventListener("change", () => { optDefinir(n, lib, c.valeur()); guarder(); });
      champs.push(c.el);
    });
    return champs.length > 0 && h("div", { class: "champ" }, h("span", { class: "titre-champ" }, f.nom), ...champs);
  }).filter(Boolean);
  return h(
    "div", { class: "options-grille" },
    h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Format de sortie"),
      h("div", { class: "liste-liens" }, FORMATS_CACHE.map((f) => caseSource({ nom: f.nom, actif: choisis.includes(f.id), onclick: () => bascule(f.id) })))),
    ...sections,
  );
}
// 3.8.02 : les 19 langues connues de suite_plan.LANGUES — le même mot, pour que le choix fermé de l'interface
// matche exactement ce que le moteur sait reconnaître.
const LANGUES = [
  "français", "anglais", "allemand", "espagnol", "italien", "néerlandais", "portugais", "polonais", "russe",
  "finnois", "suédois", "norvégien", "danois", "tchèque", "estonien", "arabe", "turc", "chinois", "japonais",
];  // fmt: skip
// Les quatre presets faisables aujourd'hui (suite_traduction.PRESETS) ; « noms propres » demande une reconnaissance
// d'entités pas encore branchée — grisé, avec « bientôt », plutôt que proposé et cassé.
const PRESETS_NE_PAS_TRADUIRE = [
  ["Mots entre guillemets", false], ["MAJUSCULES", false], ["Nombres et dates", false], ["URLs et adresses mail", false],
  ["Noms propres", true],
];  // fmt: skip

function rendreOptionsTraduction(n, refresh, guarder) {
  const entree = optLabel(n, "Langue d'entrée") || "détecter";
  const versListe = optLabel(n, "Traduire vers").split(",").map((s) => s.trim()).filter(Boolean);
  const presetsListe = optLabel(n, "Ne pas traduire").split(",").map((s) => s.trim()).filter(Boolean);
  const actif = optLabel(n, "Protéger certains mots") !== "non";
  const majEntree = (v) => { optDefinir(n, "Langue d'entrée", v); guarder(); refresh(); };
  const majVers = (l) => { optDefinir(n, "Traduire vers", l.join(", ")); guarder(); refresh(); };
  const majPresets = (l) => { optDefinir(n, "Ne pas traduire", l.join(", ")); guarder(); refresh(); };
  const majActif = (v) => { optDefinir(n, "Protéger certains mots", v); guarder(); refresh(); };
  const basculeVers = (l) => majVers(versListe.includes(l) ? versListe.filter((x) => x !== l) : [...versListe, l]);
  const basculePreset = (l) => majPresets(presetsListe.includes(l) ? presetsListe.filter((x) => x !== l) : [...presetsListe, l]);

  const champTest = champ({ libelle: "Un texte à traduire", placeholder: "ex. club FFSA" });
  const resultatTest = h("div", { class: "sortie-test", "aria-live": "polite" });
  async function tester() {
    const texte = champTest.valeur().trim();
    if (!texte) return;
    try {
      const r = await api.traductionTester({ texte, de: entree, vers: versListe, presets: actif ? presetsListe : [] });
      resultatTest.textContent = Object.entries(r.traductions).map(([v, t]) => `${v} : ${t}`).join("\n") || "Choisis au moins une langue « Traduire vers ».";
    } catch (e) {
      resultatTest.textContent = e instanceof Refus ? e.message : "Le test a échoué.";
    }
  }

  return h(
    "div", { class: "options-grille" },
    h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Langue d'entrée"),
      groupePuces([["détecter", "Détecter"], ...LANGUES.map((l) => [l, l])], entree, majEntree)),
    h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Traduire vers"),
      h("div", { class: "liste-liens" }, LANGUES.map((l) => caseSource({ nom: l, actif: versListe.includes(l), onclick: () => basculeVers(l) })))),
    h("div", { class: "champ" },
      h("span", { class: "titre-champ" }, "Ne pas traduire certains mots"),
      groupePuces([["oui", "oui"], ["non", "non"]], actif ? "oui" : "non", majActif),
      actif && h("div", { class: "liste-liens" }, PRESETS_NE_PAS_TRADUIRE.map(([l, bientot]) =>
        bientot ? puce({ libelle: `${l} · bientôt`, disabled: true }) : puce({ libelle: l, actif: presetsListe.includes(l), onclick: () => basculePreset(l) })))),
    h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Tester sur un exemple"), champTest.el,
      bouton({ libelle: `${VERBES.lancer} le test`, icon: "tester", petit: true, onclick: tester }), resultatTest),
  );
}

// 3.8.03 (Condition « si ») et 3.8.06 (Filtre, même moteur) : plusieurs lignes {champ, comparateur, valeur},
// combinées par et/ou. Stocké dans les options comme « Champ 1 »/« Comparateur 1 »/« Valeur 1 », « Champ 2 »…
const CHAMPS_CONDITION = ["nom", "ville", "pays", "genre", "origine", "site", "numéro", "fonction"];
const CHAMPS_FILTRE_SEULEMENT = ["Nombre de sources", "Fiabilité minimale"];
const COMPARATEURS = ["est égal à", "est différent de", "contient", "ne contient pas", "commence par", "finit par", "est vide", "n'est pas vide"];
// Synonymes acceptés par le moteur (suite_plan.CHAMPS) mais pas affichés comme tels : les modèles livrés « si »/« filtre »
// stockent encore « catégorie » (avant 3.8.03) — l'afficher comme « genre » évite une puce qui paraît vide à l'ouverture.
const CHAMP_SYNONYMES = { "catégorie": "genre", type: "genre", "numero officiel": "numéro", "numéro officiel": "numéro" };

function lignesConditions(n) {
  const out = [];
  let i = 1;
  while (n.opts.some(([lib]) => lib === `Champ ${i}`)) {
    out.push({ champ: optLabel(n, `Champ ${i}`), comparateur: optLabel(n, `Comparateur ${i}`) || "est égal à", valeur: optLabel(n, `Valeur ${i}`) });
    i += 1;
  }
  if (out.length) return out;
  // ancien format à une seule ligne (si/filtre d'avant 3.8.03) : lu tel quel, migré au nouveau format dès la première modification
  const champLegacy = optLabel(n, "Si le champ") || optLabel(n, "Garder si le champ");
  return [{ champ: CHAMP_SYNONYMES[champLegacy] || champLegacy, comparateur: "est égal à", valeur: optLabel(n, "est égal à") }];
}

function ecrireLignesConditions(n, lignes) {
  n.opts = n.opts.filter(([lib]) => !/^(Champ|Comparateur|Valeur) \d+$/.test(lib) && lib !== "Si le champ" && lib !== "Garder si le champ" && lib !== "est égal à");
  lignes.forEach((l, idx) => {
    const i = idx + 1;
    n.opts.push([`Champ ${i}`, l.champ], [`Comparateur ${i}`, l.comparateur], [`Valeur ${i}`, l.valeur]);
  });
}

function rendreOptionsConditions(filtre) {
  return (n, refresh, guarder) => {
    const lignes = lignesConditions(n);
    const champsChoix = filtre ? [...CHAMPS_CONDITION, ...CHAMPS_FILTRE_SEULEMENT] : CHAMPS_CONDITION;
    const mode = optLabel(n, "Combinateur") || "et";
    const maj = (l) => { ecrireLignesConditions(n, l); guarder(); refresh(); };
    const ligneVue = (l, i) => {
      const special = l.champ === "Nombre de sources" || l.champ === "Fiabilité minimale";
      const sansValeur = !special && (l.comparateur === "est vide" || l.comparateur === "n'est pas vide");
      const champValeur = champ({ libelle: special ? (l.champ === "Nombre de sources" ? "Minimum" : "Lettre A à F") : "Valeur (ou plusieurs, séparées par une virgule)", valeur: l.valeur });
      champValeur.saisie.addEventListener("change", () => { const copie = [...lignes]; copie[i] = { ...l, valeur: champValeur.valeur() }; maj(copie); });
      return h(
        "div", { class: "champ" },
        h("div", { class: "deux-col" },
          groupePuces(champsChoix.map((c) => [c, c]), l.champ, (v) => { const copie = [...lignes]; copie[i] = { ...l, champ: v }; maj(copie); }),
          !special && groupePuces(COMPARATEURS.map((c) => [c, c]), l.comparateur, (v) => { const copie = [...lignes]; copie[i] = { ...l, comparateur: v }; maj(copie); })),
        !sansValeur && champValeur.el,
        lignes.length > 1 && boutonIcone({ icon: "retirer", etiquette: "Retirer cette condition", onclick: () => maj(lignes.filter((_, j) => j !== i)) }),
      );
    };
    const maximum = filtre && champ({ libelle: "Garder au maximum", valeur: optLabel(n, "Garder au maximum"), placeholder: "sans plafond" });
    if (maximum) maximum.saisie.addEventListener("change", () => { optDefinir(n, "Garder au maximum", maximum.valeur()); guarder(); });
    return h(
      "div", { class: "options-grille" },
      lignes.length > 1 && h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Combiner les conditions"),
        groupePuces([["et", "Toutes les conditions (ET)"], ["ou", "Au moins une condition (OU)"]], mode, (v) => { optDefinir(n, "Combinateur", v); guarder(); refresh(); })),
      ...lignes.map(ligneVue),
      bouton({ libelle: `${VERBES.ajouter} une condition`, icon: "ajouter", petit: true, onclick: () => maj([...lignes, { champ: champsChoix[0], comparateur: "est égal à", valeur: "" }]) }),
      filtre && maximum.el,
    );
  };
}

// 3.8.04 : seule l'origine « Liste collée » est prête à être branchée dans le moteur ; les deux autres restent
// choisissables (le réglage se garde), avec une note honnête plutôt qu'un geste qui ne ferait rien en silence.
const ORIGINES_BOUCLE = ["Liste collée", "Fichier importé", "Résultat d'une tuile précédente"];
const REMPLACE_BOUCLE = ["le lieu cherché", "le nom cherché", "un mot-clé ajouté"];

function rendreOptionsBoucle(n, refresh, guarder) {
  const origine = optLabel(n, "Origine de la liste") || ORIGINES_BOUCLE[0];
  const remplace = optLabel(n, "Répéter pour chaque") || REMPLACE_BOUCLE[0];
  const liste = champ({ libelle: "Liste (un élément par ligne)", valeur: optLabel(n, "Liste"), lignes: 4 });
  liste.saisie.addEventListener("change", () => { optDefinir(n, "Liste", liste.valeur()); guarder(); });
  const maximum = champ({ libelle: "Maximum de tours", valeur: optLabel(n, "Maximum de tours") || "50" });
  maximum.saisie.addEventListener("change", () => { optDefinir(n, "Maximum de tours", maximum.valeur()); guarder(); });
  return h(
    "div", { class: "options-grille" },
    h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Origine de la liste"),
      groupePuces(ORIGINES_BOUCLE.map((o) => [o, o]), origine, (v) => { optDefinir(n, "Origine de la liste", v); guarder(); refresh(); })),
    origine === "Liste collée" ? liste.el : h("p", { class: "legende" }, "Pas encore branché dans le moteur : le réglage se garde, mais la recherche ne se relance pas encore pour chaque élément."),
    h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Répéter pour chaque"),
      groupePuces(REMPLACE_BOUCLE.map((r) => [r, r]), remplace, (v) => { optDefinir(n, "Répéter pour chaque", v); guarder(); refresh(); })),
    maximum.el,
  );
}

// 3.8.07 : « Attendre » a disparu (un quota qui se renouvelle vite est déjà réessayé automatiquement par le
// programme ; un quota lent ne se rattrape pas par une attente de quelques minutes) — deux choix seulement.
const CHOIX_ATTENTE = ["Sauter cette source, continuer les autres", "Arrêter toute la recherche"];

function rendreOptionsAttente(n, refresh, guarder) {
  const choix = optLabel(n, "Quand le quota est atteint") || CHOIX_ATTENTE[0];
  return h(
    "div", { class: "options-grille" },
    h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Quand le quota d'une source est atteint"),
      groupePuces(CHOIX_ATTENTE.map((c) => [c, c]), choix, (v) => { optDefinir(n, "Quand le quota est atteint", v); guarder(); refresh(); }),
      h("span", { class: "aide-champ" }, "Un quota qui se renouvelle vite (par minute) est déjà réessayé automatiquement : ce réglage ne concerne que les quotas qui ne se rattraperaient pas pendant la recherche.")),
  );
}

// 3.8.08 : le dollar disparaît, l'unité du programme est le crédit. « Budget maximum » : un montant fixe, ou
// une part du plafond mensuel déjà réglé dans Réglages. Le seuil d'alerte devient réglable (pas figé à 80).
const CHOIX_BUDGET_MAXIMUM = ["Montant fixe", "Pourcentage du plafond mensuel"];
const CHOIX_ACTION_SEUIL = ["Prévenir", "Ne rien faire"];

function rendreOptionsBudget(n, refresh, guarder) {
  const type = optLabel(n, "Budget maximum") || CHOIX_BUDGET_MAXIMUM[0];
  const montant = champ({ libelle: "Montant (crédits)", valeur: optLabel(n, "Montant (crédits)") || "5" });
  montant.saisie.addEventListener("change", () => { optDefinir(n, "Montant (crédits)", montant.valeur()); guarder(); });
  const pourcentage = champ({ libelle: "Pourcentage du plafond mensuel", valeur: optLabel(n, "Pourcentage du plafond mensuel") || "20" });
  pourcentage.saisie.addEventListener("change", () => { optDefinir(n, "Pourcentage du plafond mensuel", pourcentage.valeur()); guarder(); });
  const seuil = champ({ libelle: "À partir de (%)", valeur: optLabel(n, "À partir de") || "80" });
  seuil.saisie.addEventListener("change", () => { optDefinir(n, "À partir de", seuil.valeur()); guarder(); });
  return h(
    "div", { class: "options-grille" },
    h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Budget maximum"),
      groupePuces(CHOIX_BUDGET_MAXIMUM.map((c) => [c, c]), type, (v) => { optDefinir(n, "Budget maximum", v); guarder(); refresh(); })),
    type === CHOIX_BUDGET_MAXIMUM[0] ? montant.el : pourcentage.el,
    seuil.el,
    h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Une fois le seuil atteint"),
      groupePuces(CHOIX_ACTION_SEUIL.map((c) => [c, c]), optLabel(n, "Action") || CHOIX_ACTION_SEUIL[0], (v) => { optDefinir(n, "Action", v); guarder(); refresh(); })),
  );
}

// 3.8.09 : liste fermée mais extensible (pilote.operations_ia.vue, même principe que les formats de sortie, 3.8.01).
let OPERATIONS_IA_CACHE = null;
async function chargerOperationsIa() {
  if (!OPERATIONS_IA_CACHE) OPERATIONS_IA_CACHE = await api.operationsIa();
  return OPERATIONS_IA_CACHE;
}

function rendreOptionsIa(n, refresh, guarder) {
  if (!OPERATIONS_IA_CACHE) {
    chargerOperationsIa().then(refresh);
    return h("p", { class: "legende" }, "Les opérations arrivent…");
  }
  const operation = optLabel(n, "Opération") || OPERATIONS_IA_CACHE[0]?.nom || "";
  const modele = champ({ libelle: "Modèle", valeur: optLabel(n, "Modèle"), placeholder: "laisse vide pour le modèle par défaut de l'agent" });
  modele.saisie.addEventListener("change", () => { optDefinir(n, "Modèle", modele.valeur()); guarder(); });
  const marquer = optLabel(n, "Marquer les résultats") !== "non";
  const effort = optLabel(n, "Effort") || EFFORTS_IA[0];
  const plafond = champ({ libelle: "Traiter au maximum", valeur: optLabel(n, "Traiter au maximum"), placeholder: "laisse vide pour tout traiter", type: "number" });
  plafond.saisie.addEventListener("change", () => { optDefinir(n, "Traiter au maximum", plafond.valeur()); guarder(); });
  return h(
    "div", { class: "options-grille" },
    h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Opération"),
      groupePuces(OPERATIONS_IA_CACHE.map((o) => [o.nom, o.nom]), operation, (v) => { optDefinir(n, "Opération", v); guarder(); refresh(); }),
      h("span", { class: "aide-champ" }, OPERATIONS_IA_CACHE.find((o) => o.nom === operation)?.description || "")),
    modele.el,
    h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Effort"),
      groupePuces(EFFORTS_IA.map((e) => [e, e]), effort, (v) => { optDefinir(n, "Effort", v); guarder(); refresh(); }),
      h("span", { class: "aide-champ" }, "Plus d'effort : une réponse plus réfléchie, mais plus lente.")),
    plafond.el,
    h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Marquer les résultats"),
      groupePuces([["oui", "oui"], ["non", "non"]], marquer ? "oui" : "non", (v) => { optDefinir(n, "Marquer les résultats", v); guarder(); refresh(); }),
      h("span", { class: "aide-champ" }, "Par défaut activé : ce que l'IA produit reste marqué « IA » dans la grappe.")),
  );
}

export const RENDUS_OPTIONS = { format: rendreOptionsFormat, traduction: rendreOptionsTraduction, si: rendreOptionsConditions(false), filtre: rendreOptionsConditions(true), boucle: rendreOptionsBoucle, attente: rendreOptionsAttente, budget: rendreOptionsBudget, ia: rendreOptionsIa };
