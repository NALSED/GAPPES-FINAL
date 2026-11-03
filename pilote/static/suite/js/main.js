// Point d'entrée : la barre d'onglets, le titre de page, et le contenu de l'onglet courant. Tout le reste est dans les modules.
import { api } from "./api.js";
import { monterAide, redessinerAide } from "./aide.js";
import { h, icone } from "./dom.js";
import { app, recharger } from "./etat.js";
import { demarrerInstallation } from "./installation.js";
import { ONGLETS, PLUS_TARD, VERBES, aPluriel } from "./mots.js";
import { pageRecherche } from "./recherche.js";
import { pageTri } from "./tri.js";
import { chargerTableau, pageTableau, quitterTableau } from "./tableau.js";
import { ficheOutil, ficheSource, pageOutils, pageSources } from "./reglages.js";
import { annoncer, bouton, champ } from "./ui.js";

const ECRANS = {
  recherche: () => { app.onglet = "recherche"; },
  "recherche/simple": () => { app.onglet = "recherche"; app.recherche.ouvert.simple = true; },
  "recherche/avancee": () => { app.onglet = "recherche"; app.recherche.ouvert.adv = true; },
  "recherche/sauvegardees": () => { app.onglet = "recherche"; app.recherche.ouvert.sauvees = true; },
  tri: () => { app.onglet = "tri"; },
  "tableau-de-bord": () => { app.onglet = "tableau-de-bord"; },
  reglages: () => { app.onglet = "reglages"; },
  "reglages/sources": () => { app.onglet = "reglages"; app.reglages.sous = "sources"; },
  "reglages/outils": () => { app.onglet = "reglages"; app.reglages.sous = "outils"; },
};
app.naviguer = (ecran) => {
  (ECRANS[ecran] || ECRANS.recherche)();
  location.hash = `#/${app.onglet}`;
  app.rendre();
};

/** Charge ce qu'un onglet a besoin de charger avant de se dessiner ; quitte le Tableau de bord proprement
 * (arrête son sondage, §4) si on le laissait. */
async function entrerDans(onglet) {
  if (onglet !== "tableau-de-bord") quitterTableau();
  if (onglet === "tri") await chargerTri();
  else if (onglet === "tableau-de-bord") await chargerTableau();
  else app.rendre();
}

function barre() {
  return h("header", { class: "barre" }, h("nav", { class: "barre-in", "aria-label": "Onglets" }, h("span", { class: "marque" }, "Grappes"),
    ONGLETS.map((o) => h("button", {
      type: "button", class: "onglet", "aria-current": o.id === app.onglet ? "page" : null, "aria-disabled": o.concu ? null : "true", disabled: false,
      onclick: () => { if (!o.concu) return; app.onglet = o.id; location.hash = `#/${o.id}`; entrerDans(o.id); },
    }, icone(o.icone), o.nom, !o.concu && h("span", { class: "pastille-plus-tard" }, PLUS_TARD)))));
}

function pageReglages() {
  const d = app.data;
  const s = app.reglages;
  const nSources = d.sources.filter((x) => !x.retiree).length;
  const nAllumees = d.sources.filter((x) => !x.retiree && x.etat !== "off").length;
  const outils = d.outils.filter((o) => !o.retire);
  const nOutilsOn = outils.filter((o) => o.etat !== "off").length;
  const surSources = s.sous === "sources";
  const liste = h("div", {}, surSources ? pageSources() : pageOutils());
  const filtre = champ({ libelle: "Filtrer", valeur: s.filtre, type: "search", placeholder: "nom…" });
  // Filtrer ne redessine que la liste : redessiner toute la page ferait perdre le curseur à la personne qui tape.
  filtre.saisie.addEventListener("input", () => { s.filtre = filtre.valeur(); liste.replaceChildren(pageSources()); });
  const sous = (id, nom, icon, n) => h("button", { type: "button", "aria-pressed": String(s.sous === id), onclick: () => { s.sous = id; app.rendre(); } }, icone(icon), nom, h("span", { class: "n" }, String(n)));
  return [
    h("div", { class: "page-tete" },
      h("div", { class: "page-titre" }, h("h1", {}, "Réglages"),
        h("p", { class: "douce" }, surSources ? `${aPluriel(d.categories.length, "catégorie", "catégories")} · ${aPluriel(nSources, "source", "sources")} · ${nAllumees} allumée${nAllumees > 1 ? "s" : ""}` : `${aPluriel(outils.length, "outil", "outils")} · ${nOutilsOn} allumé${nOutilsOn > 1 ? "s" : ""}`)),
      h("div", { class: "lancer-ligne" }, surSources && filtre.el, bouton({ libelle: surSources ? `${VERBES.ajouter} une source` : `${VERBES.ajouter} un outil`, icon: "ajouter", variante: "principal", onclick: () => (surSources ? ficheSource() : ficheOutil()) }))),
    h("div", { class: "sous", role: "group", "aria-label": "Sous-parties de Réglages" }, sous("sources", "Sources", "source", nSources), sous("outils", "Outils", "outil", outils.length)),
    liste,
  ];
}

function pageRechercheTete() {
  return [h("div", { class: "page-tete" }, h("div", { class: "page-titre" }, h("h1", {}, "Recherche"))), pageRecherche()];
}

function dessiner() {
  const racine = document.getElementById("app");
  const haut = window.scrollY;
  racine.replaceChildren(barre(), h("main", { class: "page" }, h("div", { class: "page-in" }, app.onglet === "reglages" ? pageReglages() : app.onglet === "tri" ? pageTri() : app.onglet === "tableau-de-bord" ? pageTableau() : pageRechercheTete())),
    h("footer", { class: "pied" }, h("a", { href: "/" }, "Ancienne interface (Lancement, Tri)")));
  window.scrollTo(0, haut);
  redessinerAide();
}
app.rendre = dessiner;

async function chargerTri() {
  app.tri.donnees = null;
  app.rendre();
  try {
    app.tri.donnees = await api.tri();
  } catch (e) {
    app.tri.donnees = { a_examiner: [], tranches: [] };
    annoncer(e.message, true);
  }
  app.rendre();
}

function depuisHash() {
  const m = location.hash.match(/^#\/(recherche|reglages|tri|tableau-de-bord)/);
  app.onglet = m ? m[1] : "reglages";
}
window.addEventListener("hashchange", () => { depuisHash(); entrerDans(app.onglet); });

(async function demarrer() {
  depuisHash();
  try {
    app.data = await api.etat();
  } catch (e) {
    document.getElementById("app").replaceChildren(h("p", { class: "message-refus" }, e.message));
    return;
  }
  if (app.data.premiere_installation) {
    await demarrerInstallation();
    return;
  }
  if (app.onglet === "tri") await chargerTri();
  else if (app.onglet === "tableau-de-bord") await chargerTableau();
  else dessiner();
  monterAide();
})();

export { recharger };
