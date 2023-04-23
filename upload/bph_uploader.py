#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uploader import Uploader
import os

input_directory = [
    r'D:\CSSM_PIX\PRODUCTION\EXPORT_DATA\AdcoExportEan',
    r'D:\CSSM_PIX\PRODUCTION\EXPORT_DATA\KPIAdCo\VisuelsFournisseurs',
    r'D:\CSSM_PIX\PRODUCTION\EXPORT_DATA\KPIAdCo\CertificatsBio',    
    r'D:\CSSM_PIX\PRODUCTION\EXPORT_DATA\ExportFichesReparabilite',
    r'D:\CSSM_PIX\PRODUCTION\EXPORT_DATA\MDD_Drive'
]

for input_dir in input_directory:
    if input_dir == r'D:\CSSM_PIX\PRODUCTION\EXPORT_DATA\AdcoExportEan':
        print(input_dir)    
        parent_folder_id ='1LwfxGY084EP5cLK7ho9kMCfx6LaCqR6H'
    elif input_dir == r'D:\CSSM_PIX\PRODUCTION\EXPORT_DATA\KPIAdCo\CertificatsBio':
        print(input_dir)
        parent_folder_id ='1W57Ooit9Bjnd2-1A2JnZ7HT7or4Kyz-C'
    elif input_dir == r'D:\CSSM_PIX\PRODUCTION\EXPORT_DATA\KPIAdCo\VisuelsFournisseurs':
        print(input_dir)      
        parent_folder_id = '1_uO9vyEV5pc1D0REIx4sNF6gnZacCBfH'
    elif input_dir == r'D:\CSSM_PIX\PRODUCTION\EXPORT_DATA\ExportFichesReparabilite':
        print(input_dir)    
        parent_folder_id = '1Bl2cBP9I1msh2WMqpb1K2fTNf0V_gq1V'
    elif input_dir == r'D:\CSSM_PIX\PRODUCTION\EXPORT_DATA\MDD_Drive':
        print(input_dir)
        parent_folder_id = '1I2GI0aItdCpjgtUydADZaO7mEvluNIzQ'
    
    u = Uploader()
    result = u.uploadFolder(input_dir, max_depth=10, parentId=parent_folder_id)
    print(result)
    
certificatBio_input_dir = r'D:\CSSM_PIX\PRODUCTION\EXPORT_DATA\CertificatsBio'
certificatBio_parent_folder_name = "CAMPAGNE_EN_COURS"
certificatBio_parent_folder_id = '12AyqWzeNeoEO8yoy0d7CIR-my-TdDE_5'    
u = Uploader()
#u.delete_folder(folder_name=certificatBio_parent_folder_name, parent_folder_id='1hKWcSkky8lvUYmC5IRj-k_YLLu8Cyws4')
result = u.uploadFolder(certificatBio_input_dir, max_depth=10, parentId=certificatBio_parent_folder_id)	
print(result)
