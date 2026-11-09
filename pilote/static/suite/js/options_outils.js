// Rendu des options d'un outil par genre de modèle livré (3.8.0X) : remplace le champ texte générique par un
// vrai composant quand le genre en a un. Partagé entre plan.js (tuile posée sur le plan de travail) et
// reglages.js (fiche de réglage par défaut de l'outil, dans Réglages › Outils) : une seule source de vérité
// pour les vocabulaires fermés, pour que les deux écrans ne divergent plus jamais (spécification 905 § 1).
//
// `n` est n'importe quel objet exposant `.opts` (liste [libellé, valeur]) ; `guarder` est appelé après chaque
// mutation pour que l'appelant persiste à sa façon (sauvegarde immédiate du plan, ou rien : la fiche outil ne
// persiste qu'au clic sur Enregistrer).
import { api, apiAssistant, Refus } from "./api.js";
import { h } from "./dom.js";
import { app } from "./etat.js";
import { EFFORTS_IA, VERBES } from "./mots.js";
import { bouton, boutonIcone, carteRepliable, champ, groupePuces, menu, menuMultiple, puce } from "./ui.js";

export const genreDeOutil = (o) => (o && o.nature !== "script" ? o.modele || o.id : null);

let FORMATS_CACHE = null;
async function chargerFormats() {
  if (!FORMATS_CACHE) FORMATS_CACHE = await api.formats();
  return FORMATS_CACHE;
}

// 6.3 (retour du 08/11/2026) : la destination des fichiers de sortie n'a nulle part où s'afficher dans /suite —
// c'est un réglage GÉNÉRAL (vaut pour tout export, pas propre à une tuile), partagé avec l'ancienne page
// (`reglages.sortie.dossier`, déjà lu par `sortie.dossier_de_sortie()`) : on réutilise sa route plutôt que
// d'inventer un second stockage propre à cette tuile.
let SORTIE_CACHE = null;
async function chargerSortie() {
  if (!SORTIE_CACHE) SORTIE_CACHE = (await apiAssistant.reglages()).sortie || { dossier: "" };
  return SORTIE_CACHE;
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
  if (!FORMATS_CACHE || !SORTIE_CACHE) {
    Promise.all([chargerFormats(), chargerSortie()]).then(refresh);
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
  // 6.2 (règle 3.10) : un bloc repliable par format (modèle des blocs de Réglages / Sources) au lieu d'une
  // liste de neuf cases suivie de sections empilées — la liste reste courte fermée, les réglages d'un format se
  // lisent en le dépliant. Déplier/replier LE format l'active/le désactive : pas de double case à cocher.
  const cartes = FORMATS_CACHE.map((f) => {
    const actif = choisis.includes(f.id);
    const champs = [];
    if (actif && f.contenus.length > 1) {
      const lib = `${f.nom} : contenu`;
      champs.push(h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Contenu"),
        groupePuces(f.contenus.map((c) => [c, c]), optLabel(n, lib) || f.contenus_defaut[0], (v) => { optDefinir(n, lib, v); guarder(); refresh(); })));
    }
    if (actif && f.id === "csv") {
      const lib = "Séparateur";
      champs.push(h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Séparateur"),
        groupePuces([[";", ";"], [",", ","]], optLabel(n, lib) || ";", (v) => { optDefinir(n, lib, v); guarder(); refresh(); })));
    }
    if (actif) (f.besoin || []).forEach((champBesoin) => {
      const lib = `${f.nom} : ${champBesoin}`;
      const c = champ({ libelle: `${f.nom} — ${champBesoin}`, valeur: optLabel(n, lib), placeholder: champBesoin === "url" ? "https://…" : "" });
      c.saisie.addEventListener("change", () => { optDefinir(n, lib, c.valeur()); guarder(); });
      champs.push(c.el);
    });
    return carteRepliable({
      titre: f.nom, compte: actif ? "activé" : null, ouverte: actif,
      onbascule: () => bascule(f.id),
      corps: actif ? h("div", { class: "options-grille" }, ...champs) : null,
    });
  });
  const destChamp = champ({
    libelle: "Destination des fichiers de sortie", valeur: SORTIE_CACHE.dossier || "",
    placeholder: "/chemin/absolu/vers/un/dossier — vide : chaque recherche garde son propre dossier",
  });
  const destMessage = h("div", { class: "sortie-test", "aria-live": "polite" });
  async function enregistrerDest() {
    try {
      const r = await apiAssistant.definirSortie({ dossier: destChamp.valeur().trim() });
      SORTIE_CACHE.dossier = r.dossier;
      destMessage.textContent = r.dossier ? `Enregistré : les fichiers s'écriront dans « ${r.dossier} ».` : "Enregistré : chaque recherche garde son propre dossier.";
    } catch (e) {
      destMessage.textContent = e instanceof Refus ? e.message : "Le dossier n'a pas pu être enregistré.";
    }
  }
  return h(
    "div", { class: "options-grille" },
    h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Format de sortie")),
    ...cartes,
    h("div", { class: "champ" }, destChamp.el,
      bouton({ libelle: "Enregistrer la destination", icon: "tester", petit: true, onclick: enregistrerDest }), destMessage,
      h("span", { class: "aide-champ" }, "Vérifié avant l'enregistrement (le dossier existe, ou son ancêtre est accessible en écriture). Vaut pour tous les exports, pas seulement ce format.")),
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
  // 7.3 (retour du 08/11/2026) : « Langue d'entrée » devient multiple, au sens « détecte uniquement parmi ces
  // langues-là » (un seul appel de traduction par texte, comme avant) ; « Traduire vers » reprend le même
  // composant visuel — les deux listes de langues se règlent désormais de la même façon (menu déroulant à choix
  // multiple, règle 3.10 : 19 langues).
  const entreeListe = optLabel(n, "Langue d'entrée").split(",").map((s) => s.trim()).filter(Boolean);
  const versListe = optLabel(n, "Traduire vers").split(",").map((s) => s.trim()).filter(Boolean);
  const presetsListe = optLabel(n, "Ne pas traduire").split(",").map((s) => s.trim()).filter(Boolean);
  const actif = optLabel(n, "Protéger certains mots") !== "non";
  const majEntree = (l) => { optDefinir(n, "Langue d'entrée", l.join(", ")); guarder(); refresh(); };
  const majVers = (l) => { optDefinir(n, "Traduire vers", l.join(", ")); guarder(); refresh(); };
  const majPresets = (l) => { optDefinir(n, "Ne pas traduire", l.join(", ")); guarder(); refresh(); };
  const majActif = (v) => { optDefinir(n, "Protéger certains mots", v); guarder(); refresh(); };
  const basculePreset = (l) => majPresets(presetsListe.includes(l) ? presetsListe.filter((x) => x !== l) : [...presetsListe, l]);

  const champTest = champ({ libelle: "Un texte à traduire", placeholder: "ex. club FFSA" });
  const resultatTest = h("div", { class: "sortie-test", "aria-live": "polite" });
  async function tester() {
    const texte = champTest.valeur().trim();
    if (!texte) return;
    try {
      const r = await api.traductionTester({ texte, de: entreeListe[0] || "détecter", vers: versListe, presets: actif ? presetsListe : [] });
      resultatTest.textContent = Object.entries(r.traductions).map(([v, t]) => `${v} : ${t}`).join("\n") || "Choisis au moins une langue « Traduire vers ».";
    } catch (e) {
      resultatTest.textContent = e instanceof Refus ? e.message : "Le test a échoué.";
    }
  }

  return h(
    "div", { class: "options-grille" },
    h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Langue d'entrée"),
      menuMultiple(LANGUES.map((l) => [l, l]), entreeListe, majEntree),
      h("span", { class: "aide-champ" }, entreeListe.length ? "La détection se limite à ces langues-là." : "Aucune choisie : la détection n'est pas restreinte.")),
    h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Traduire vers"),
      menuMultiple(LANGUES.map((l) => [l, l]), versListe, majVers)),
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
    // 8.1 (règle 3.10) : champ (8 ou 10 choix) et comparateur (8 choix) en menus déroulants plutôt qu'en pastilles
    // — une condition = une ligne, au lieu de 16 à 18 pastilles empilées pour une seule condition.
    const ligneVue = (l, i) => {
      const special = l.champ === "Nombre de sources" || l.champ === "Fiabilité minimale";
      const sansValeur = !special && (l.comparateur === "est vide" || l.comparateur === "n'est pas vide");
      const champValeur = champ({ libelle: special ? (l.champ === "Nombre de sources" ? "Minimum" : "Lettre A à F") : "Valeur (ou plusieurs, séparées par une virgule)", valeur: l.valeur });
      champValeur.saisie.addEventListener("change", () => { const copie = [...lignes]; copie[i] = { ...l, valeur: champValeur.valeur() }; maj(copie); });
      return h(
        "div", { class: "champ" },
        h("div", { class: "trois-col" },
          menu(champsChoix.map((c) => [c, c]), l.champ, (v) => { const copie = [...lignes]; copie[i] = { ...l, champ: v }; maj(copie); }),
          !special && menu(COMPARATEURS.map((c) => [c, c]), l.comparateur, (v) => { const copie = [...lignes]; copie[i] = { ...l, comparateur: v }; maj(copie); }),
          !sansValeur && champValeur.el),
        lignes.length > 1 && boutonIcone({ icon: "retirer", etiquette: "Retirer cette condition", onclick: () => maj(lignes.filter((_, j) => j !== i)) }),
      );
    };
    const maximum = filtre && champ({ libelle: "Garder au maximum", valeur: optLabel(n, "Garder au maximum"), placeholder: "sans plafond" });
    if (maximum) maximum.saisie.addEventListener("change", () => { optDefinir(n, "Garder au maximum", maximum.valeur()); guarder(); });
    // 11.1 : Filtre et Condition « si » sont visuellement des jumeaux (même nombre apparent de pastilles) alors
    // que leurs trois différences réelles — nombre de sorties en premier, c'est ce qui change l'usage sur le plan —
    // ne se voyaient nulle part. Dites ici, pour qu'on sache en ouvrant la fiche lequel des deux on règle.
    const sorties = filtre
      ? h("p", { class: "legende" }, "Une seule sortie : ce qui passe la condition (les autres résultats sont écartés).")
      : h("p", { class: "legende" }, "Deux sorties : « oui » et « non ». Les deux se branchent séparément sur le plan.");
    return h(
      "div", { class: "options-grille" },
      sorties,
      lignes.length > 1 && h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Combiner les conditions"),
        groupePuces([["et", "Toutes les conditions (ET)"], ["ou", "Au moins une condition (OU)"]], mode, (v) => { optDefinir(n, "Combinateur", v); guarder(); refresh(); })),
      ...lignes.map(ligneVue),
      bouton({ libelle: `${VERBES.ajouter} une condition`, icon: "ajouter", petit: true, onclick: () => maj([...lignes, { champ: champsChoix[0], comparateur: "est égal à", valeur: "" }]) }),
      filtre && maximum.el,
    );
  };
}

// 3.8.04 : AUCUNE des trois origines ne relance encore réellement la recherche (QUESTIONS.md, addendum du
// 09/11/2026 : relu le 08/11, « Liste collée » n'est pas davantage branchée que les deux autres — le dossier
// de travail unique par recherche, que plusieurs modules supposent, doit être revu dans une session dédiée
// avec un moteur grappes accessible). Les trois restent choisissables (le réglage se garde), avec la même
// note honnête pour les trois plutôt qu'un geste qui ne ferait rien en silence pour une seule d'entre elles.
const ORIGINES_BOUCLE = ["Liste collée", "Fichier importé", "Résultat d'une tuile précédente"];
const REMPLACE_BOUCLE = ["le lieu cherché", "le nom cherché", "un mot-clé ajouté"];

function rendreOptionsBoucle(n, refresh, guarder) {
  const origine = optLabel(n, "Origine de la liste") || ORIGINES_BOUCLE[0];
  const remplace = optLabel(n, "Répéter pour chaque") || REMPLACE_BOUCLE[0];
  const liste = champ({ libelle: "Liste (un élément par ligne)", valeur: optLabel(n, "Liste"), lignes: 4 });
  liste.saisie.addEventListener("change", () => { optDefinir(n, "Liste", liste.valeur()); guarder(); refresh(); });
  const maximum = champ({ libelle: "Maximum de tours", valeur: optLabel(n, "Maximum de tours") || "50" });
  maximum.saisie.addEventListener("change", () => { optDefinir(n, "Maximum de tours", maximum.valeur()); guarder(); });
  // 9.3 (retour du 08/11/2026) : rien ne montrait ce que la boucle produirait. Aperçu des premières recherches,
  // construit à partir de la liste et de la saisie courante — sans rien lancer (toujours vrai, 9.1 ci-dessus).
  const elements = (origine === "Liste collée" ? liste.valeur() : "").split("\n").map((v) => v.trim()).filter(Boolean);
  const saisieBase = (app.data?.plan?.saisie || "").trim();
  const apercu = elements.length
    ? h("p", { class: "legende" },
        `${elements.length} élément${elements.length > 1 ? "s" : ""} → ` +
        elements.slice(0, 5).map((e) => `« ${[saisieBase, e].filter(Boolean).join(" ")} »`).join(", ") +
        (elements.length > 5 ? "…" : ""))
    : null;
  return h(
    "div", { class: "options-grille" },
    h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Origine de la liste"),
      groupePuces(ORIGINES_BOUCLE.map((o) => [o, o]), origine, (v) => { optDefinir(n, "Origine de la liste", v); guarder(); refresh(); })),
    origine === "Liste collée" ? liste.el : null,
    h("p", { class: "legende" }, "Pas encore branché dans le moteur : le réglage se garde, mais la recherche ne se relance pas encore pour chaque élément."),
    // 9.2 : le libellé dit maintenant le remplacement (le code interne le nomme déjà REMPLACE_BOUCLE).
    h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Chaque élément de la liste remplace"),
      groupePuces(REMPLACE_BOUCLE.map((r) => [r, r]), remplace, (v) => { optDefinir(n, "Répéter pour chaque", v); guarder(); refresh(); })),
    apercu,
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

// 10.2 (retour du 08/11/2026) : « Même entité si » et « En cas de doublon, garder » sont des choix fermés
// (SEUILS_FUSION, suite_plan.py) oubliés de ce registre à sa création (905 §1) — ils tombaient sur le champ
// texte libre générique, avec repli silencieux du moteur sur une faute de frappe. *large* regroupe davantage,
// au risque de confondre deux entités ; *strict* ne propose que les quasi-certitudes, au risque de laisser
// passer de vrais doublons.
const NIVEAUX_FUSION = [
  ["Large", "Regroupe plus largement : moins de doublons manqués, au risque de confondre deux entités différentes."],
  ["Normal", "Réglage équilibré, par défaut."],
  ["Strict", "Ne propose que les quasi-certitudes, au risque de laisser passer de vrais doublons."],
];  // fmt: skip
const CHOIX_GARDER_FUSION = ["la plus récente", "la première trouvée", "la plus fiable"];

function rendreOptionsFusion(n, refresh, guarder) {
  const niveau = optLabel(n, "Même entité si") || "Normal";
  const garder = optLabel(n, "En cas de doublon, garder") || CHOIX_GARDER_FUSION[2];
  return h(
    "div", { class: "options-grille" },
    h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Même entité si"),
      groupePuces(NIVEAUX_FUSION.map(([l]) => [l, l]), niveau, (v) => { optDefinir(n, "Même entité si", v); guarder(); refresh(); }),
      h("span", { class: "aide-champ" }, NIVEAUX_FUSION.find(([l]) => l === niveau)?.[1] || "")),
    h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "En cas de doublon, garder"),
      groupePuces(CHOIX_GARDER_FUSION.map((c) => [c, c]), garder, (v) => { optDefinir(n, "En cas de doublon, garder", v); guarder(); refresh(); })),
  );
}

// 10.2, même oubli : l'intervalle de rafraîchissement de RSSHub est aussi une liste fermée (pas encore
// consommée par le moteur, qui ne lit que « Site à transformer » — le réglage se garde en attendant).
const INTERVALLES_RSSHUB = ["15 minutes", "30 minutes", "1 heure", "4 heures"];

function rendreOptionsRsshub(n, refresh, guarder) {
  const site = champ({ libelle: "Site à transformer", valeur: optLabel(n, "Site à transformer"), placeholder: "https://www.exemple.fr/rubrique" });
  site.saisie.addEventListener("change", () => { optDefinir(n, "Site à transformer", site.valeur()); guarder(); });
  const intervalle = optLabel(n, "Rafraîchir toutes les") || INTERVALLES_RSSHUB[1];
  return h(
    "div", { class: "options-grille" },
    site.el,
    h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Rafraîchir toutes les"),
      groupePuces(INTERVALLES_RSSHUB.map((c) => [c, c]), intervalle, (v) => { optDefinir(n, "Rafraîchir toutes les", v); guarder(); refresh(); })),
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
  // 12.3 (08/11/2026) : le champ « Modèle » disparaît — le modèle est l'agent Claude installé sur la machine,
  // point ; on verra plus tard s'il doit revenir. Le réglage se garde en base s'il existait déjà, juste plus édité ici.
  const marquer = optLabel(n, "Marquer les résultats") !== "non";
  const effort = optLabel(n, "Effort") || EFFORTS_IA[0];
  // 12.4 : « Traiter au maximum » ne disait ni qu'il s'agit de FICHES, ni ce qu'il advient des autres (elles
  // passent sans être touchées) — les deux sont dites dans le libellé et son aide.
  const plafond = champ({ libelle: "Traiter au maximum (fiches)", valeur: optLabel(n, "Traiter au maximum"), placeholder: "laisse vide pour toutes les traiter", type: "number" });
  plafond.saisie.addEventListener("change", () => { optDefinir(n, "Traiter au maximum", plafond.valeur()); guarder(); });
  // 12.2 : « Classer / catégoriser » ne range tout dans « autre » que parce qu'aucun champ ne permet de saisir
  // ses catégories — ajouté seulement pour cette opération, pour ne pas encombrer les deux autres qui n'en ont pas besoin.
  const estClasser = operation === "Classer / catégoriser";
  const categories = estClasser ? champ({ libelle: "Catégories (séparées par une virgule)", valeur: optLabel(n, "Catégories"), placeholder: "ex. association, entreprise, administration" }) : null;
  if (categories) categories.saisie.addEventListener("change", () => { optDefinir(n, "Catégories", categories.valeur()); guarder(); });
  return h(
    "div", { class: "options-grille" },
    h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Opération"),
      groupePuces(OPERATIONS_IA_CACHE.map((o) => [o.nom, o.nom]), operation, (v) => { optDefinir(n, "Opération", v); guarder(); refresh(); }),
      h("span", { class: "aide-champ" }, OPERATIONS_IA_CACHE.find((o) => o.nom === operation)?.description || "")),
    categories && h("div", { class: "champ" }, categories.el,
      h("span", { class: "aide-champ" }, "Sans cette liste, l'opération ne peut pas être lancée.")),
    h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Effort"),
      groupePuces(EFFORTS_IA.map((e) => [e, e]), effort, (v) => { optDefinir(n, "Effort", v); guarder(); refresh(); }),
      h("span", { class: "aide-champ" }, "Plus d'effort : une réponse plus réfléchie, mais plus lente.")),
    h("div", { class: "champ" }, plafond.el,
      h("span", { class: "aide-champ" }, "Les fiches au-delà de cette limite passent sans être touchées par l'IA.")),
    h("div", { class: "champ" }, h("span", { class: "titre-champ" }, "Marquer les résultats"),
      groupePuces([["oui", "oui"], ["non", "non"]], marquer ? "oui" : "non", (v) => { optDefinir(n, "Marquer les résultats", v); guarder(); refresh(); }),
      h("span", { class: "aide-champ" }, "Par défaut activé : ce que l'IA produit reste marqué « IA » dans la grappe.")),
  );
}

export const RENDUS_OPTIONS = { format: rendreOptionsFormat, traduction: rendreOptionsTraduction, si: rendreOptionsConditions(false), filtre: rendreOptionsConditions(true), boucle: rendreOptionsBoucle, attente: rendreOptionsAttente, budget: rendreOptionsBudget, ia: rendreOptionsIa, fusion: rendreOptionsFusion, rsshub: rendreOptionsRsshub };
