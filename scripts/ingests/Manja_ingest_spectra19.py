from scripts.ingests.ingest_utils import *
from scripts.ingests.utils import *

SAVE_DB = False  # save the data files in addition to modifying the .db file
RECREATE_DB = True  # recreates the .db file from the data files

logger.setLevel(logging.INFO)

db = load_simpledb('SIMPLE.db', recreatedb=RECREATE_DB)

# Read in CSV file as Astropy table
data = Table.read('scripts/ingests/Manja19_spectra9.csv')

# Ingest new instrumentation and telescope and mode

ingest_instrument(db, telescope='HST', instrument='WFC3', mode='G141 grism')

# Ingest new publications
ingest_publication(db, doi='10.1038/nature08245')
ingest_publication(db, doi='10.1093/pasj/62.6.L61')
ingest_publication(db, doi='10.1111/j.1365-2966.2009.14763.x')
ingest_publication(db, doi='10.1093/mnras/stw1969')
ingest_publication(db, doi='10.1051/0004-6361/201117081')
ingest_publication(db, doi='10.1093/mnras/stu1715')
ingest_publication(db, doi='10.1086/519793', publication='ODon07')
ingest_publication(db, bibcode='2011AAS...21710304R ')
ingest_publication(db, doi='10.1086/312458')
ingest_publication(db, doi='10.1086/586735')
ingest_publication(db, doi='10.1088/2041-8205/798/1/L13') # Yang15
ingest_publication(db, doi='10.3847/1538-3881/aaa5a6') # Bill18
# Update Buen15a to Buen15
ingest_publication(db, doi='10.3847/2041-8205/829/2/L32') #Lew_16
ingest_publication(db, doi='10.1088/0004-637X/768/2/121') # Apai13
ingest_publication(db, doi='10.1088/2041-8205/760/2/L31') # Buen12
ingest_publication(db, doi='10.3847/0004-637X/826/1/8') # Yang16

ingest_sources(db, 'NAME Luhman 16A', 'Luhm13', search_db=False)
ingest_sources(db, 'NAME Luhman 16B', 'Luhm13', search_db=False)

ingest_sources(db, data['Source'], data['discovery reference'])

# Fixing missing reference for Luhman 16
db.Sources.update().where(db.Sources.c.source == 'Luhman 16').values(reference='Luhm13').execute()

# Add the spectra to the database
ingest_spectra(db, data['Source'], data['Spectrum'], 'em.IR.NIR', 'HST', 'WFC3', 'G141 grism',
               data['observation_date'],
               'Manj19', 'micron', 'erg/cm2/s/A', comments=data['spectrum comments'],
               other_references=data['Other specturm refs'])

# WRITE THE JSON FILES
if SAVE_DB:
    db.save_database(directory='data/')
