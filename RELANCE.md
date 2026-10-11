# RELANCE (interruption du serveur tmux, cause probablement un redemarrage ou une coupure)

## 1. Etat des lieux avant de reprendre
Tu as des modifications non committees (donnees/.journal_ccr.log, outils/corpus_synthetique.py).
Verifie-les (`git diff`), decide toi-meme si tu les completes et les committes ou si tu les
annules proprement, puis note la decision dans DECISIONS.md.

## 2. Reprise
FINAL.md reste la reference unique. Reprends a l'etape ou tu t'es arrete, dans l'ordre de son
paragraphe 14 (corpus synthetique a 3 grappes -> test de bout en bout jusqu'a resultat.csv ->
robustesse et charge -> amorcage -> recuperateur de pages -> ingestion automatique -> boucle
`grappes cycle` -> rapport).

## 3. Nouveau livrable : bilan des economies de jetons
Cree `outils/bilan_jetons.py` et le rapport `ECONOMIES.md`, regenerable par une commande.
Sources : `donnees/.journal_ccr.log` (appels routes vers le compte gratuit) et les traces du
hook RTK. Le rapport contient :
- nombre d'appels routes vers le compte gratuit, periode couverte, volume estime ;
- gain RTK cumule, en rappelant explicitement que `rtk gain` est une ESTIMATION, pas une mesure ;
- total consolide, avec la marge d'incertitude ;
- une ligne par jour, et le detail des hypotheses de calcul.
Regles : aucune valeur inventee ; une donnee absente est affichee comme absente, jamais estimee
a la place ; si une source est vide ou illisible, le rapport le dit et continue.
Ajoute des tests : journal vide, ligne malformee, periode sans appel.
Documente dans docs/utilisateur.md et lie le rapport depuis ETAT.md.

## 4. Compte rendu
Mets a jour ETAT.md. La section « En attente de Sednal » ne contient que : sujet(s),
cles des fournisseurs, limites, activation de `autonome`.
Ne lance aucune collecte reelle tant que `autonome: true` n'est pas mis.
