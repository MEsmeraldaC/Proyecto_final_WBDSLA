Hola, 

El siguiente código esta basado en el código proporcionado por ATGenomics. 

El siguiente código tiene como objetivo principal 
*   Búsqueda de secuencias codificantes de proteínas asociadas a la resistencia antimicrobiana en *Pseudomonas aeruginosa*.

Para ello se requiere de la instalación de los siguientes paquetes:
*	**Pandas** para manejo general de datos 
*	**pyCirclize** para visualizar nuestros datos genómicos
*	**pyrodigal** para la predicción de genes codificantes
*	**requests** para interactuar con las APIs de NCBI, UniProt e InterProScan
*	**seaborn** para visualizar algunas de las propiedades genómicas obtenidas
*	**subprocess** ejecutar comandos fuera del entorno de python
*	**BioPython** para el manejo de secuencias
*	**io** para conectar las entradas y salidas de los distintos programas
Un archivo credentials.py donde se almacene las llaves de acceso para la API de NCBI.
Además de la instalación local de BLAST+, se puede obtener mayor información a tráves del siguiente link: https://www.ncbi.nlm.nih.gov/books/NBK569861/ y el paquete a descargar de acuerdo a su sistemas operativo aqui ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/

En el código 
