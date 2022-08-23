
from pandas import to_datetime
import os
import warnings
warnings.filterwarnings('ignore')
from astropy.table import Table
from astropy import units as u
from astropy.time import Time
from compileheaderV1 import *


table_file='/Users/jolie/gitlocation/rewrite spectra/Manja14_spectra_adjusted.csv'
data = Table.read(table_file)
original_data_dir = '/Users/jolie/gitlocation/rewrite spectra/ISAAC_Manjavacas2014' #where the old fits files are
fits_data_dir = '/Users/jolie/gitlocation/rewrite spectra/Manj14' #where we want the new fits files to go
#goes through table of data
#this is the part where you input values for each variable

for row in data:
    object_name = row['Source'] #row is defined so it loops through each row to
    #logger.debug(f'source: {object}')

    spectrum_url = row['Spectrum'] #goes to specific column entry finds the url

    url_data = fits.getdata(spectrum_url)
    spectrum_table = Table(url_data)
    file = os.path.basename(spectrum_url)

    full_name = (original_data_dir + file)



    history1 = f'Original file: {file}' #gives orginal name of file
    history2 = 'This file generated by SIMPLE-db/scripts/ingests/rewrite_spectra.py'  #shows where file came from
    history = (history1 +', ' + history2)
    #pass history into the funciton as a tuple and then change it to be a list in the fits files header/function

    wavelength_unit = u.micron   #using astropy to define units
    flux_unit = u.erg/u.cm/u.cm/u.s/u.Angstrom

    comment1 = 'Manja14 FITS file did not provide flux uncertainty'
    comment = (comment1) #add next comment no tuple bc fits file does not want an iterable item

    wavelength_data = spectrum_table['col1'] * wavelength_unit   #multiplying everythign by untis to convert


    #All the key words should be in one dictionary to pass to the function to write the header
    #REQUIRED KEY WORDSW

    #turn these into a dictionary
    header_dict = {
        'VOCLASS' : 'Spectrum-1.0',
        'VOPUB' : 'SIMPLE Archive' ,
        'title' : 'ISAAC Spectra of Brown Dwarfs from Manjavacas et. al. 2014' ,
        'RA' : row['RA'] , #from the vizier catalog, put in csv table
        'dec' : row['dec'] , #from the vizier catalog, put in csv table
        'time' : (Time(to_datetime(row['start time'])).jd + Time(to_datetime(row['stop time'])).jd) /2,
        'exposure_time' : row['exposure time'] ,
        'bandpass' : 'JHK' ,#get from paper
        'aperture' :'0.3' ,
        'object_name' : object_name,

        #OTHER KEYWORDS
        'time_start' : Time(to_datetime(row['start time'])).jd , #turns dates into accepetable format then converts to Time object then to MJD
        'time_stop' : Time(to_datetime(row['stop time'])).jd , #dates r orginally in month day, year
        'bibcode' : '2014A&A...564A..55M' ,
        'instrument' : row['instrument'] ,
        'obs_date' : to_datetime(row['observation_date']) ,
        'author' : 'Manjavacas, E. ; Bonnefoy, M. ; Schlieder, J. E. ; Allard, F. ; Rojo, P. ; Goldman, B. ; Chauvin, G. ; Homeier, D. ; Lodieu, N. ; Henning, T.',
        'reference_doi' : '10.1051/0004-6361/201323016'  ,
        'telescope' : row['telescope'] ,
        'history' : history ,
        'wavelength' : wavelength_data , #multiplying everythign by untis to convert
        'wavelength_units' : f"[{wavelength_data.unit:FITS}]",
        'width' : (max(wavelength_data).value - min(wavelength_data.value)),
        'min_wave' : min(wavelength_data).value,
        'max_wave' : max(wavelength_data).value,
        'flux' : tuple(spectrum_table['col1'].data) * flux_unit, # spectrum_table['col1'] * flux_unit,
        # flux_unc : 'took out flux uncertainty'  #TOOK OUT FLUX_UNC BC MANJA 14 ONLY HAD 2 COLUMNS
        'comment': comment
        }

    #only 1 columns, does not have flux uncertaitnty


    spectrum_data_out = Table({'wavelength': spectrum_table['col0'] * wavelength_unit , 'flux':spectrum_table['col1'] * flux_unit }) #TOOK OUT FLUX_UNC

    hdu1 = fits.BinTableHDU(data = spectrum_data_out)

    hdu1.header['EXTNAME'] = 'SPECTRUM' #prints out different headers
    hdu1.header.set('Spectrum', str(object_name), 'Object Name')





    hdu0 = fits.PrimaryHDU(header=compile_header(**header_dict)) #not sure what this menas

    spectrum_mef = fits.HDUList([hdu0,hdu1])#hdu0 is header and hdu1 is data

    file_root = os.path.splitext(file)[0] #split the path name into a pair root and ext so the root is just the ext [0] is the name of the file wihtout the .csv
    fits_filename = fits_data_dir + file_root + '.fits' #turns into fits files by putting it in new folder that we defined at begining and adding name of file then .fits
    try:
        spectrum_mef.writeto(fits_filename, overwrite=True)
        # SHOULD BE: spectrum.write(fits_filename, format='tabular-fits', overwrite=True, update_header=True)
        #logger.info(f'Wrote {fits_filename}')
    except:
        raise ValueError
