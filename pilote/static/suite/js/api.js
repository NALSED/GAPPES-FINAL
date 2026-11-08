// Appels au serveur de pilote. Une erreur rend la phrase en français du serveur, telle quelle.
export class Refus extends Error {
  constructor(message, statut = 0, corps = null) {
    super(message);
    this.statut = statut;
    this.corps = corps; // la réponse du serveur, pour un 409 (avertissement à lire avant d'allumer)
  }
}

async function requete(methode, chemin, corps) {
  let rep;
  try {
    rep = await fetch(chemin, {
      method: methode,
      headers: corps === undefined ? {} : { "Content-Type": "application/json" },
      body: corps === undefined ? undefined : JSON.stringify(corps),
    });
  } catch {
    throw new Refus("Le serveur de pilote ne répond pas.");
  }
  let json = null;
  try {
    json = await rep.json();
  } catch {
    /* corps vide */
  }
  if (!rep.ok) {
    const d = json && json.detail;
    throw new Refus(typeof d === "string" ? d : "La demande a été refusée.", rep.status, d);
  }
  return json;
}

function appel(methode, chemin, corps) {
  return requete(methode, `/api/suite${chemin}`, corps);
}

export const api = {
  etat: () => appel("GET", "/etat"),
  tri: () => appel("GET", "/tri"),
  get: (chemin) => appel("GET", chemin),
  post: (chemin, corps = {}) => appel("POST", chemin, corps),
  put: (chemin, corps = {}) => appel("PUT", chemin, corps),
  supprimer: (chemin) => appel("DELETE", chemin),
  aide: (fonction, corps = {}) => appel("POST", `/aide/${fonction}`, corps),
  aideGet: (chemin) => appel("GET", `/aide/${chemin}`),
  formats: () => requete("GET", "/api/formats"), // registre des formats de sortie (pilote.formats.vue, pas sous /api/suite)
  operationsIa: () => requete("GET", "/api/operations_ia"), // registre des opérations de l'Assistant IA, même principe
  // Tableau de bord (1.1) : routes partagées avec l'ancienne interface, sous /api/ et non /api/suite/.
  recherches: () => requete("GET", "/api/recherches"),
  recherche: (rid) => requete("GET", `/api/recherches/${rid}`),
  arreterRecherche: (rid) => requete("POST", `/api/recherches/${rid}/arret`),
  programmes: () => requete("GET", "/api/programmes"),
  journal: (rid) => requete("GET", rid ? `/api/journal?recherche=${rid}` : "/api/journal"),
  traductionTester: (corps) => appel("POST", "/traduction/tester", corps),
};

/** Les routes de l'assistant de première installation : les mêmes que la page classique (`/`), sous `/api/` et non `/api/suite/`
 *  (D-assistant-suite : on réutilise les routes éprouvées ce matin plutôt que d'en recréer sous `/api/suite`). */
export const apiAssistant = {
  reglages: () => requete("GET", "/api/reglages"),
  presetsPersonnaliser: (corps) => requete("POST", "/api/presets/personnaliser", corps),
  definirCle: (nom, corps) => requete("PUT", `/api/cles/${nom}`, corps),
  modifierSource: (id, corps) => requete("PUT", `/api/reglages/source/${id}`, corps),
  definirSortie: (corps) => requete("PUT", "/api/reglages/sortie", corps),
  testerSource: (id) => requete("POST", `/api/sources/${id}/tester`, {}),
  terminer: (corps) => requete("POST", "/api/assistant/terminer", corps),
};
