# Activation

Sednal a fourni les 4 elements :
- config/sujets.yaml : un sujet, "Les acteurs de l'actualite francaise en ce moment".
- config/autonomie.yaml : quotas, profondeur, interdits, autonome: true.
- La cle Tavily est dans config/secrets.env (TAVILY_API_KEY), hors depot, droits 600,
  ignoree par git. Charge-la en variable d'environnement a l'execution (ex. python-dotenv),
  jamais en dur dans le code ni dans les journaux.

Verifie d'abord que Tavily est bien branche comme fournisseur dans la multiprise (config YAML
du fournisseur, § 4 de FINAL.md). Si ce n'est pas encore fait, fais-le avant de lancer quoi
que ce soit.

Lance un premier `grappes cycle` reel, en respectant les quotas et les regles de FINAL.md
(robots.txt, delai, pas de connexion, journal de chaque appel). Rends compte dans
rapports/cycle_<date>.md et dans ETAT.md : ce qui a ete trouve, combien de sources confirmees,
combien de probables, et si les hypotheses sur les formats (Q16 a Q19) se confirment ou non
sur ces vraies donnees. Si un indicateur de stabilite declenche un retour en arriere, dis-le
clairement dans le rapport.
