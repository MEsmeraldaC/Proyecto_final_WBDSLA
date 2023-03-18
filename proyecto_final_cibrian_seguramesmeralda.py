# -*- coding: utf-8 -*-
"""Proyecto_final_Cibrian_SeguraMEsmeralda.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1cjsSOft-p_GzhXxnhMvdn02qjEgZ-oxg

##Proyecto final para CAMP Women in Bioinformatics and Data Science. 

Elaborado por Marcela Esmeralda Cibrian Segura, el siguiente trabajo esta basado en el ejemplo 1 de ATGenomics.

El objetivo principal del presente trabajo es 


*   Busqueda de secuencias codificantes de proteínas asociadas a la resistencia antimicrobiana en *Pseudomonas aeruginosa*. 


Los objetivos especificos son:


*   Predicción de genes en genomas bacterianos.
*   Búsqueda de secuencias proteícas en bases de datos.
*   Búsqueda de secuencias homólogas usando BLAST.
*   Búsqueda de dominios funcionales en proteinas seleccionadas.

#Preparación del entorno

Para que el notebook funcione adecuadamente se debe llenar el archivo credentials.py con un correo electrónico y la API key que proporciona NCBI a sus usuarios registrados. 

Con el siguiente código cargamos las bibliotecas necesarias para que todo el código del notebook funcione.

Para ello se requiere de la instalación de los siguientes paquetes:
*	**Pandas** para manejo general de datos 
*	**pyCirclize** para visualizar nuestros datos genómicos
*	**pyrodigal** para la predicción de genes codificantes
*	**requests** para interactuar con las APIs de NCBI, UniProt e InterProScan
*	**seaborn** para visualizar algunas de las propiedades genómicas obtenidas
*	**subprocess** ejecutar comandos fuera del entorno de python
*	**BioPython** para el manejo de secuencias
*	**io** para conectar las entradas y salidas de los distintos programas

Además de la instalación local de BLAST+, se puede obtener mayor información a tráves del siguiente link: https://www.ncbi.nlm.nih.gov/books/NBK569861/ y el paquete a descargar de acuerdo a su sistemas operativo aqui ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/

Para la instalación de las bibliotecas mencionadas puede ejecutar los siguientes comandos:
"""

pip3 install matplotlib
pip3 install pandas
pip3 install pycirclize
pip3 install pyrodigal
pip3 install requests
pip3 install seaborn
pip3 install biopython

import credentials
import pandas as pd
import matplotlib.pyplot as plt
import numpy  as np
import pyrodigal
import requests
import seaborn as sns
import subprocess
import sys
from Bio import SeqIO
from Bio import Entrez
from io                 import StringIO
from matplotlib.patches import Patch
from pycirclize         import Circos
from pycirclize.parser  import Gff
from requests.adapters  import HTTPAdapter, Retry

"""#1. Obtención de una secuencia genómica. 

Se busco en el NCBI-Genome utilizando el filtro de genoma completo a *Pseudomonas aeruginosa*, que se sabe que es un organismo ambiental Gram-negativo común. Puede ser un factor patógeno significativo de infecciones graves en humanos, especialmente en pacientes con fibrosis quística. Debido a su **resistencia natural** a los antibióticos y la capacidad de formar biopelículas, la infección por este patógeno puede causar graves problemas terapéuticos. Por lo tanto se buscaran genes asociados a la resistencia antimicrobiana de esta especie. 

Para este caso se utilizó el ensamble ASM76324v3, y se buscó genes de resistencia antibioticos en el cromosoma con número de acceso CP021380.2.

Con el siguiente código se puede descargar el genoma en formato genbank.
"""

accession = "CP021380.2"
genome = Entrez.efetch(db="nucleotide",
                       id=accession,
                       format="gb",
                       rettype="text")
record = SeqIO.read(genome, "genbank")
genome_length = len(record.seq)

"""#2. Predicción de genes usando pyrodigal

En este paso se ocupó pyrodigal que se puede integrar facilmente en python. 

Con el siguiente código, almacenó las secuencias aminoacídicas de los genes predichos en un nuevo archivo CP021380.2.faa y las coordenadas de los genes predichos en un archivo CP021380.2.gff. 

Para el genoma de *Pseudomonas aeruginosa* se utilizó el prefijo Pseudomonas_a.
"""

orf_finder = pyrodigal.OrfFinder()
orf_finder.train(bytes(record.seq))
orf_genes  = orf_finder.find_genes(bytes(record.seq))

aa_file = accession + ".faa"
prefix  = "Pseudomonas_a"
with open(aa_file, "w") as orf_gene:
    orf_genes.write_translations(orf_gene,sequence_id=prefix)

gff_file = accession + ".gff"
prefix  = "Pseudomonas_a"
with open(gff_file, "w") as orf_gene:
    orf_genes.write_gff(orf_gene,sequence_id=prefix)

"""#3.Obtención de un set de secuencias de referencia

Se utilizó la API de UniProt para poder descargar los genes de referencia de la resistencia a antibioticos. Para ello se utilizó request para mantener todo nuestro código en el notebook de python. Asi como también con el siguiente código podemos descargar secuencias de UniProt en el objeto uniprot_ref_seqs. 

En el query se incluye la seccion de de **reviewed** oara aumentar la confiabilidad de los resultados.
"""

uniprot_api_url  = "https://rest.uniprot.org/uniprotkb/stream"
uniprot_api_args = {"compressed" : "false",
                    "format"     : "fasta",
                    "query"      : "(antibiotic resistance) AND (reviewed:true)"}
uniprot_ref_seqs = requests.get(uniprot_api_url,params=uniprot_api_args).text

"""#4. Creación de una base de datos tipo BLAST

A partir de las secuencias aminoacídicas de las predicciones de pyrodigal, se creo una base de datos tipo BLAST que se utilizó para pescar secuencias similares a las secuencias obtenidas en UniProt.
"""

uniprot_seqs_file = open("uniprot_sequences.fasta", "wt")
uniprot_seqs_file.write(uniprot_ref_seqs)
uniprot_seqs_file.close()

! head uniprot_sequences.fasta

"""Para la variable makeblastdb_path se debera poner la direccion donde se encuentre su programa de "makeblastdb"."""

makeblastdb_path = "/home/esme/Descargas/ncbi-blast-2.13.0+/bin/makeblastdb"
makeblastdb_command = [makeblastdb_path,'-in',aa_file,'-dbtype','prot']
subprocess.call(makeblastdb_command)

#Building a new DB, current time: 03/16/2023 19:15:07
#New DB name:   /home/esme/Descargas/CP021380.2.faa
#New DB title:  CP021380.2.faa
#Sequence type: Protein
#Deleted existing Protein BLAST database named /home/esme/Descargas/CP021380.2.faa
#Keep MBits: T
#Maximum file size: 3000000000B
#Adding sequences from FASTA; added 6324 sequences in 0.150203 seconds.


0

"""#5. Obtención de secuencias de interés en el genoma analizado"""

blastp_path       = "/home/esme/Descargas/ncbi-blast-2.13.0+/bin/blastp"
blastp_out_format = "6 qseqid sseqid qlen slen qstart sstart qend send score evalue length positive"
blastp_out_file   = accession + ".blast.tsv"
blastp_command    = [blastp_path,
                     "-db",          aa_file,
                     "-query",       "uniprot_sequences.fasta",
                     "-evalue",      "1e-9",
                     "-out",         blastp_out_file,
                     "-outfmt",      blastp_out_format,
                     "-num_threads", "8"]
subprocess.call(blastp_command)

0

"""En código anterior llama a BLAST y se obtuvo una tabla .tsv con los resultados de la comparación. """

makeblastdb_path = "/home/esme/Descargas/ncbi-blast-2.13.0+/bin/makeblastdb"
makeblastdb_command = [makeblastdb_path,'-in',"uniprot_sequences.fasta",'-dbtype','prot']
subprocess.call(makeblastdb_command)
blastp_path      = "/home/esme/Descargas/ncbi-blast-2.13.0+/bin/blastp"
blast_out_format = "6 qseqid sseqid qlen slen qstart sstart qend send score evalue length positive"
blast_out_file   = "uniprot_sequences.blast.tsv"
blastp_command   = [blastp_path,
                    "-db",          "uniprot_sequences.fasta",
                    "-query",       aa_file,
                    "-evalue",      "1e-9",
                    "-out",         blast_out_file,
                    "-outfmt",      blast_out_format,
                    "-num_threads", "8"]
subprocess.call(blastp_command)

#Building a new DB, current time: 03/16/2023 19:38:14
#New DB name:   /home/esme/Descargas/uniprot_sequences.fasta
#New DB title:  uniprot_sequences.fasta
#Sequence type: Protein
#Deleted existing Protein BLAST database named /home/esme/Descargas/uniprot_sequences.fasta
#Keep MBits: T
#Maximum file size: 3000000000B
#Adding sequences from FASTA; added 2714 sequences in 0.0612409 seconds.


0

"""De igual forma se realizó la comparación de las secuencias obtenidas del genoma contra las secuencias de Uniprot, usando el código anterior. El resultado que arroja es que se añaden 2714 secuencias al FASTA que estan relacionados con la resistencia antimicrobiana. """



"""#6. Examinación de los resultados de la búsqueda tipo BLAST

Con el siguiente código se le da formato al dataframe que se obtuvo del BLAST y se importó a Pandas para poder empezar a ver los resultados y hacer "limpieza".
"""

blastp_column_names = blastp_out_format.split(" ")[1:]
blastp_df = pd.read_csv(blastp_out_file,sep="\t",names=blastp_column_names)
blastp_df

"""En el genoma de interés encontramos 722 proteínas potencialmente asociadas con resistencia a antibioticos, no obstante, no todas las secuencias podrían ser de nuestro interés"""

candidate_genes=blastp_df["sseqid"].unique().tolist()
len(candidate_genes)
#722

"""A través de la biblioteca pyCirclize podemos visualizar los genes que fueron identificados en el paso anterior, pero primero debemos transformar la información que tenemos a un formato legible para pyCirclize. """

gff_columns     = ["chr","source","feature_type","start","end","score","strand","phase","info"]
gff_df          = pd.read_csv(gff_file,sep="\t",comment="#",header=None,names=gff_columns)
gff_df["start"] = gff_df["start"].astype(int)
gff_df["end"]   = gff_df["end"].astype(int)

gff_df

"""Con el siguiente código definimos una funcion que nos ayuda a separar el texto de la columna "info" del dataframe anterior y sea más facil de manejar con Pandas. """

def get_gff_info(info_str):
    out_dict = {}
    info_arr = info_str.split(";")
    for line in info_arr:
        if "=" in line:
            line_arr    = line.split("=")
            field_name  = line_arr[0]
            field_value = line_arr[1]
            out_dict[field_name] = field_value
    return out_dict

gff_df["annotation"] = gff_df["info"].apply(lambda x: get_gff_info(x))

gff_df["annotation"][0]["ID"]
#'Pseudomonas_a_1'

"""Filtrado de datos para incluir solamente los genes identificados como asociados a la resistencia antimicrobiana."""

gff_df["candidate"] = gff_df["annotation"].apply(lambda x: "include" if x["ID"] in candidate_genes else "exclude")

gff_df

"""6.1.4 El resultado lo almacenamos en un nuevo archivo gff para que pyCirclize visualice unicamente los genes de interés"""

candidate_df = gff_df.copy()
candidate_df = candidate_df[candidate_df["candidate"]=="include"][gff_columns]
candidate_df.to_csv("candidates.gff",sep="\t",header=False,index=False)
candidate_df

"""6.1.5 Visualización de los datos con pyCirclize. 

Con el siguiente código construiremos distintos objetos para obtener un mapa circular que nos permitirá identificar manualmente potenciales operones en el genoma de *Pseudomonas aeruginosa*
"""

circos = Circos(sectors={accession: genome_length})
circos.text("Pseudomonas aeruginosa")
circos_gff = Gff(gff_file="candidates.gff")
sector = circos.get_sector(accession)
sector = circos.sectors[0]
cds_track = sector.add_track((80, 100))
cds_track.axis(fc="#EEEEEE", ec="none")
cds_track.genomic_features(circos_gff.extract_features("CDS", target_strand =  1), r_lim=(90, 100),fc="red" )
cds_track.genomic_features(circos_gff.extract_features("CDS", target_strand = -1), r_lim=(80,  90),fc="blue")
pos_list, labels = [], []
cds_track.xticks_by_interval(
    interval=500000,
    label_formatter=lambda label_value: f"{label_value/ 1000000:.1f} Mb",
    label_orientation="vertical")
fig = circos.plotfig().set_figwidth(5)

"""Visualización de los datos con seaborn

De igual forma se realizó una examinación más exhaustiva, con seadborn con una  serie de swarmplots en donde podemos comparar las posiciones de los genes en el dataframe completo, separando por categorias ("genes candidatos" vs "genes no candidatos") y por cadena ("+" vs "-").

Con esta aproximación podemos identificar un par de operones enriquecido en genes candidatos, siendo el operón ubicado en la cadena negativa entre 0.6 Mbp y 0.8 Mbp
"""

num_bins = 25
counter_1 = 0
counter_2 = 0
fig, axes = plt.subplots(5,5,figsize=(30,30))
bin_len  = (genome_length - (genome_length % (num_bins - 1))) / (num_bins)
for bin_num in range(num_bins):
    start_pos = bin_num * bin_len
    end_pos   = (bin_num + 1) * bin_len
    mb_df = gff_df.copy()
    mb_df = mb_df[(mb_df["start"]>start_pos) & (mb_df["end"]<=end_pos)]
    sns.swarmplot(ax = axes[counter_1,counter_2],data = mb_df,y="candidate",x="start",hue="strand",dodge=True,order=["exclude","include"],hue_order=["+","-"])
    axes[counter_1,counter_2].set(ylabel=None)
    counter_2 += 1
    if (counter_2%5 == 0):
        counter_2 = 0
        counter_1 += 1
plt.show()

"""Como se observa en ambos graficos en la en el intervalo de 0.6-0.8 Mb se puede distinguir un posibles genes relacionado con la resistencia a antiobioticos en este microorganismo.

#7. Examinación a detalle del genes seleccionados

Los genomas procarióticos están usualmente organizados en unidades operacionales llamadas operones, en donde los genes se encuentran muy proximos entre sí y en la misma cadena de DNA. Sin embargo, en la resistencia a antibioticos se sabe que se relacionan con elementos genéticos móviles, como plásmidos, transposones e integrones. Por lo que en este caso no se buscará un operón en especifico pero si los genes que se encuentran relacionados con la resistencia.
"""

operon_df = gff_df.copy()
operon_df = operon_df[(operon_df["start"]     >= 600000) &
                      (operon_df["end"]       <= 800000) &
                      (operon_df["strand"]    == "-")     &
                      (operon_df["candidate"] == "include")]
operon_df.reset_index(drop=True, inplace=True)

len(operon_df)
#6

operon_gene_list = []
for index in operon_df.index.tolist():
    gene_id = operon_df["annotation"][index]["ID"]
    operon_gene_list.append(gene_id)

operon_gene_list
#['Psedomonas_a_591',
# 'Psedomonas_a_608',
# 'Psedomonas_a_673',
# 'Psedomonas_a_681',
# 'Psedomonas_a_730',
# 'Psedomonas_a_733']

"""Posteriormente, construiremos un string que contendrá las secuencias aminoacídicas de los genes de interés en formato fasta. 

Este string lo enviaremos al servicio web de InterProScan para buscar dominios conservados en nuestras proteínas. Eliminando los astericos de las secuencias. 

"""

query_str = ""

for record in SeqIO.parse(aa_file, "fasta"):
    seq_id  = record.id
    if(seq_id in operon_gene_list):
        seq_str = str(record.seq)
        query_str+=">"+seq_id+"\n"+seq_str+"\n"
query_str = query_str.replace("*","")

"""El proceso de búsqueda de dominios lo dividiremos en tres etapas:


*   Envío de las secuencias
*   Consulta del status del envío
*   Descarga de resultados

Cada etapa tiene una URL específica la cual definiremos a continuación
"""

submit_url   = "https://www.ebi.ac.uk/Tools/services/rest/iprscan5/run"
progress_url = "https://www.ebi.ac.uk/Tools/services/rest/iprscan5/status"
results_url  = "https://www.ebi.ac.uk/Tools/services/rest/iprscan5/result"

submit_headers   = {"Accept":"text/plain"}
progress_headers = {"Accept":"text/plain"}
results_headers  = {"Accept":"text/tab-separated-values"}

"""Se construyo un diccionario de python que se adjunto a requests para buscar los dominios funcionales."""

submit_data = {"email":"esmemarcela@gmail.com",
               "title":"operon_591_733",
               "goterms":"false",
               "pathways":"false",
               "stype":"p",
               "sequence":query_str}

submit_request = requests.post(submit_url,data=submit_data,headers=submit_headers)

"""La API de InterProScan entrega un código de estado y un job_id.
> El código de salida del servidor web, nos indican si la solicitud fue exitosa:
>>*   1xx informational response – the request was received, continuing process
*     2xx successful – the request was successfully received, understood, and accepted
*     3xx redirection – further action needs to be taken in order to complete the request
*     4xx client error – the request contains bad syntax or cannot be fulfilled
5xx server error – the server failed to fulfil an apparently valid request
"""

submit_status_code = submit_request.status_code
submit_job_id      = submit_request.text

print(submit_status_code)
print(submit_job_id)
#200
#iprscan5-R20230317-063355-0367-69284551-p1m

progress_request     = requests.get(progress_url+"/"+submit_job_id,headers=progress_headers)
progress_status_code = progress_request.status_code
progress_status      = progress_request.text
print(progress_status_code)
print(progress_status)
#200
#FINISHED

"""Si se obtiene 200 la consulta fue exitosa. """

results_log_request = requests.get(results_url+"/"+submit_job_id+"/log",headers=results_headers)
results_tsv_request = requests.get(results_url+"/"+submit_job_id+"/tsv",headers=results_headers)

print(results_log_request.text)
#17/03/2023 06:33:10:457 Welcome to InterProScan-5.61-93.0
#17/03/2023 06:33:10:458 Running InterProScan v5 in STANDALONE mode... on Linux
#17/03/2023 06:33:18:425 RunID: hh-wp-01-06.ebi.ac.uk_20230317_063318132_kgst
#17/03/2023 06:33:31:523 Loading file /nfs/public/rw/es/projects/wp-jdispatcher/logs/prod/sources/jobs/iprscan5/rest/20230317/0632/iprscan5-R20230317-063355-0367-69284551-p1m.sequence
#17/03/2023 06:33:31:525 Running the following analyses:
#[AntiFam-7.0,CDD-3.20,Coils-2.2.1,FunFam-4.3.0,Gene3D-4.3.0,Hamap-2021_04,MobiDBLite-2.0,PANTHER-17.0,Pfam-35.0,Phobius-1.01,PIRSF-3.10,PIRSR-2021_05,PRINTS-42.0,ProSitePatterns-2022_05,ProSiteProfiles-2022_05,SFLD-4,SignalP_EUK-4.1,SignalP_GRAM_NEGATIVE-4.1,SignalP_GRAM_POSITIVE-4.1,SMART-9.0,SUPERFAMILY-1.75,TIGRFAM-15.0,TMHMM-2.0c]
#Available matches will be retrieved from the pre-calculated match lookup service.

#Matches for any sequences that are not represented in the lookup service will be calculated locally.
#17/03/2023 06:33:37:090 27% completed
#17/03/2023 06:33:49:220 54% completed
#17/03/2023 06:33:55:577 81% completed
#17/03/2023 06:33:56:103 90% completed
#17/03/2023 06:34:01:735 100% done:  InterProScan analyses completed 

#2023-03-17 06:34:02,241 [main] [uk.ac.ebi.interpro.scan.jms.master.AbstractMaster:259] WARN - Master process unable to delete temporary directory /nfs/public/rw/es/projects/wp-jdispatcher/logs/prod/sources/jobs/iprscan5/rest/20230317/0632/temp/hh-wp-01-06.ebi.ac.uk_20230317_063318132_kgst

results_tsv_str = StringIO(results_tsv_request.text)
results_column_names = ["sequence","md5","length","database","accession","description","start","end","evalue","post_processed","date","entry","name"]
results_df = pd.read_csv(results_tsv_str,sep="\t",names=results_column_names)
results_df
#Se obtiene una tabla con las secuencias candidatas para la resistencia antibioticas, se puede observar que la longitud de las secuencias son cortas por lo que se puede intuir que son plasmidos.

"""#8. Conclusiones

De acuerdo a los resultados generados de este análisis se puede decir que es una herramienta clave para la búsqueda de genes en diferentes bases de datos como Genome-NCBI y UniProt con código, sin necesidad de interactuar con la pagina web. La aproximación que se realizó fue adecuada para cumplir el objetivo, sin embargo no se encontró como un operón si no mas bien los genes relacionados con  la resistencia antiobioticos que  provienen de elementos geneticos móviles como plasmidos, integrones o transposones; en este caso se observa que principalmente que son genes de enzimas como la Short-chain dehydrogenase/reductase SDR. 

Por otra parte gracias a este código se pudo descargar, predecir y comparar secuencias de un genoma con genomas de referencia en diferentes bancos de genes. Además de que se pudo visualizar en graficos de pyCirclize y seaborn de manera mas detallada los resultados y poder hacer una filtración posterior de los datos y solo obtener una tabla con los posibles genes asociados a las proteinas de interés.
"""