#!/bin/env python

import warnings
warnings.filterwarnings("ignore")
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as image
from cartopy import crs
import cartopy.feature as cfeature
import pandas as pd
import numpy as np
import xarray as xr
from datetime import datetime, timedelta
import concurrent.futures as cf
from PIL import Image
import cmaps
import io
import os, sys
#import ipdb

# set number of threads to low number
os.environ['OPENBLAS_NUM_THREADS']='15'

imageDir='/scratch2/NCEPDEV/stmp1/Deanna.Spindler/images/gfs-waves/GEFS'

WantPool=True
#maxjobs=6
maxjobs=20

#-------------------------------------
# figure optimization and compression 
#-------------------------------------
def saveImage(imagefile,**kwargs):
    ram = io.BytesIO()
    plt.gcf().savefig(ram,**kwargs)
    ram.seek(0)
    im=Image.open(ram)
    im2 = im.convert('RGB').convert('P', palette=Image.ADAPTIVE,colors=256)
    im.save(imagefile, format='PNG',optimize=True)
    ram.close()
    return
#----------------------------------------------------------------------
def add_mmab_logos(alpha=1.0):
    """
    -----------------------------------------------
    add NOAA and NWS logos to an existing figure
    as well as some branding and dates
    -----------------------------------------------
    """
    noaa_logo=image.imread('/scratch2/NCEPDEV/ocean/Deanna.Spindler/save/Logos/NOAA_logo.png')
    nws_logo=image.imread('/scratch2/NCEPDEV/ocean/Deanna.Spindler/save/Logos/NWS_logo.png')
    fig=plt.gcf()
    fig.figimage(noaa_logo,alpha=alpha,
        yo=fig.get_figheight()*fig.dpi-noaa_logo.shape[0])
    fig.figimage(nws_logo,alpha=alpha,
        xo=fig.get_figwidth()*fig.get_dpi()-nws_logo.shape[1],
        yo=fig.get_figheight()*fig.get_dpi()-nws_logo.shape[0])
    plt.annotate('NCEP/EMC/Verification Post Processing Product Generation Branch',
        xy=(0.01,0.01),xycoords='figure fraction',
        horizontalalignment='left',fontsize='x-small')
    plt.annotate(f'{datetime.now():%d %b %Y} on $Hera$',
        xy=(0.99,0.01),xycoords='figure fraction',
        horizontalalignment='right',fontsize='x-small')
    
    return
#----------------------------------------------------------------------
def plot_map(data,region,params):    
    """
    general purpose field plotting routine
    expects a DataArray with a single forecast and cycle, all data internal
    """

    print('processing',data.vDate,region['name'],data.cycle,data.fcst.values)

    data2=data.copy()
    data2['longitude']=data2.longitude+360.
    data=xr.concat([data,data2],dim='longitude')
        
    data=data.where((data.longitude>=region['lonlat'][0]) & (data.longitude<region['lonlat'][1]) &
                    (data.latitude>=region['lonlat'][2]) & (data.latitude<region['lonlat'][3]),drop=True)
                         
    plt.rc('axes', labelsize='small')    # fontsize of the x and y labels
    plt.rc('xtick', labelsize='x-small')    # fontsize of the tick labels
    plt.rc('ytick', labelsize='x-small')    # fontsize of the tick labels
    
    # all wave and wind directions reference true north, not 0 radians
    #scaled with wind speed
    uwind=data.WIND_surface.to_masked_array()*np.sin(np.radians(data.WDIR_surface.to_masked_array()-180.))
    vwind=data.WIND_surface.to_masked_array()*np.cos(np.radians(data.WDIR_surface.to_masked_array()-180.))

    # unit direction vector
    uwwave=np.sin(np.radians(data.WVDIR_surface.to_masked_array()-180.))
    vwwave=np.cos(np.radians(data.WVDIR_surface.to_masked_array()-180.))

    # unit direction vector
    uwave=np.sin(np.radians(data.DIRPW_surface.to_masked_array()-180.))
    vwave=np.cos(np.radians(data.DIRPW_surface.to_masked_array()-180.))
    
    lons=data.HTSGW_surface.longitude.values
    lats=data.HTSGW_surface.latitude.values
        
    for param in params:
            
        fig=plt.figure(dpi=200)
        central_longitude=(region['lonlat'][0]+region['lonlat'][1])/2.
        proj=region['crs'](central_longitude=central_longitude)
        ax=plt.axes(projection=proj)
        #if region['name'] != 'Global':
        #    ax.set_extent(region['lonlat'],crs=proj)
        
        WANT_QUIVER=False
        WANT_BARB=False
        if param=='HTSGW_surface':
            WANT_QUIVER=True
            WANT_BARB=True
            u=uwave
            v=vwave
            qlabel='Primary Wave Direction (unscaled)'
            qcolor='red'
        elif param=='PERPW_surface':
            WANT_QUIVER=True
            WANT_BARB=False
            u=uwave
            v=vwave            
            qlabel='Primary Wave Direction (unscaled)'
            qcolor='black'
        elif param=='SWELL_surface' or param=='SWPER_surface':
            WANT_QUIVER=False
            WANT_BARB=False
        elif param=='WVHGT_surface' or param=='WVPER_surface':
            WANT_QUIVER=True
            WANT_BARB=False
            u=uwwave
            v=vwwave
            qlabel='Wind Wave Direction (unscaled)'
            qcolor='black'
        elif param=='WIND_surface':
            WANT_QUIVER=False
            WANT_BARB=True            
        
        if WANT_QUIVER:
            ax.plot(np.nan,np.nan,'-',color=qcolor,label=qlabel,linewidth=0.5)
        if WANT_BARB:
            ax.plot(np.nan,np.nan,'-',color='black',label='Wind Barbs',linewidth=0.5)
        if WANT_QUIVER or WANT_BARB:
            ax.legend(loc='lower center',fontsize='xx-small',ncol=2)
            
        skip=np.int(np.round(lons.size/40))
        if WANT_QUIVER:
            # normalize the wave direction vectors
            u=u/np.sqrt(u**2 + v**2);
            v=v/np.sqrt(u**2 + v**2);
            ax.quiver(lons[::skip],lats[::skip],
                u[::skip,::skip],v[::skip,::skip],
                scale_units='inches',scale=12.,color='r',
                transform=crs.PlateCarree(),zorder=2)
        if WANT_BARB:
            ax.barbs(lons[::skip],lats[::skip],
                uwind[::skip,::skip],vwind[::skip,::skip],
                length=3,color='black',
                transform=crs.PlateCarree(),linewidth=0.3,zorder=3)
        #ax.coastlines()
        ax.add_feature(cfeature.LAND)
        ax.add_feature(cfeature.COASTLINE,linewidth=0.5)
        gl=ax.gridlines(draw_labels=True)
        gl.xlabel_style = {'size': 'x-small'}        
        gl.ylabel_style = {'size': 'x-small'}        
        if region['name']=='Global':
            gl.right_labels=False
            gl.top_labels=False
            
        data.ICEC_surface.plot(cmap='spring',transform=crs.PlateCarree(),zorder=1.,add_colorbar=False)
        #data[param].plot(cmap='jet',transform=crs.PlateCarree(),zorder=0.,
        #    vmin=data.vlims[param][0],vmax=data.vlims[param][1],cbar_kwargs={'shrink':0.8})
        data[param].plot.contourf(levels=vlims[param],cmap=cmaps.BlAqGrYeOrRe,transform=crs.PlateCarree(),zorder=0.,
            cbar_kwargs={'shrink':0.8,'extend':'both','ticks':vlims[param]})
                                        
        #cb.ax.tick_params(labelsize='small')
        plt.annotate('Sea Ice Concentration > 15% is shown in pink to yellow',
                     (0.5,0.05),xycoords='figure fraction',fontsize='small',
                     horizontalalignment='center')
        title=f'GEFS {data.dataType.upper()} {region["name"].replace("_"," ")} {data[param].long_name}\n{data.vDate:%Y%m%d} t{data.cycle:02n}z {data.fcst.values:03n}h fcst   Max: {data[param].max().values:0.2f}'
        plt.title(title,fontsize='small')
        add_mmab_logos()
        if not os.path.exists(f'{imageDir}/{data.vDate:%Y%m%d}'):
            os.makedirs(f'{imageDir}/{data.vDate:%Y%m%d}')
        plt.savefig(f'{imageDir}/{data.vDate:%Y%m%d}/GEFS_{region["name"].lower()}_{param}_{data.dataType}_t{data.cycle:02n}z_f{data.fcst.values:03n}.png',dpi=200)
        #saveImage(f'{imageDir}/{data.vDate:%Y%m%d}/GEFS_{region["name"].lower()}_{param}_{data.dataType}_t{data.cycle:02n}z_f{data.fcst.values:03n}.png',dpi=200)
        plt.close()
    return
        
#----------------------------------------------------------------------
if __name__=='__main__':

    theDate=pd.Timestamp(sys.argv[1])
    dataDir='/scratch2/NCEPDEV/ocean/Deanna.Spindler/noscrub/GEFS_grib/archive'
    dataTypes=['c00','mean','prob','spread']
    cycles=range(0,24,6)
    params=['HTSGW_surface','PERPW_surface','WVHGT_surface','WVPER_surface',
            'WIND_surface','SWELL_surface','SWPER_surface']    
    regions={'global':{'name':'Global','lonlat':[0,360,-90,90],'crs':crs.Miller},
             'ak':{'name':'Alaskan_Waters','lonlat':[160,230,40,85],'crs':crs.Miller},
             'atl':{'name':'Atlantic','lonlat':[255,420,-75,75],'crs':crs.Miller},
             'aus':{'name':'Australia-Indonesia','lonlat':[60,180,-60,40],'crs':crs.Miller},
             'npac':{'name':'North_Atlantic','lonlat':[260,376,-10,80],'crs':crs.Miller},
             'gmex':{'name':'Gulf_of_Mexico','lonlat':[262,282,14,32],'crs':crs.Miller},
             'hawaii':{'name':'Hawaii','lonlat':[197,208,15,26],'crs':crs.Miller},
             'indian':{'name':'Indian_Ocean','lonlat':[20,130,-72,28],'crs':crs.Miller},
             'natl':{'name':'North_Atlantic','lonlat':[260,376,-10,80],'crs':crs.Miller},
             'npac':{'name':'North_Pacific','lonlat':[110,250,-10,82],'crs':crs.Miller},
             'neatl':{'name':'Northeast_Atlantic','lonlat':[330,385,40,78],'crs':crs.Miller},
             'nepac':{'name':'Northeast_Pacific','lonlat':[160,250,0,80],'crs':crs.Miller},
             'nwatl':{'name':'Northwest_Atlantic','lonlat':[260,322,0,80],'crs':crs.Miller},
             'pac':{'name':'Pacific','lonlat':[110,290,-78,78],'crs':crs.Miller},
             'useast':{'name':'US_East_Coast','lonlat':[275,306,20,46],'crs':crs.Miller},
             'keyw':{'name':'Key_West','lonlat':[274,282,21,29],'crs':crs.Miller},
             'prico':{'name':'Puerto_Rico','lonlat':[290,297,15,22],'crs':crs.Miller},
             'zoom1':{'name':'US_West_Coast_Zoom_1','lonlat':[223,237,39,51],'crs':crs.Miller},
             'zoom2':{'name':'US_West_Coast_Zoom_2','lonlat':[230,244,29,41],'crs':crs.Miller}, 
             'arctic':{'name':'Arctic','lonlat':[0,360,55,90],'crs':crs.NorthPolarStereo},
             'antarc':{'name':'Antarctic','lonlat':[0,360,-90,-30],'crs':crs.SouthPolarStereo}}
        
    dataType=dataTypes[1]

    """
    # load all cycles to get vmin/vmax
    fnames=f'{dataDir}/{theDate:%Y%m%d}/nc/gefs.wave.t*z.{dataType}.global.0p25.f*.nc'
    data=xr.open_mfdataset(fnames)
    vlims={}
    for param in params:
        vlims[param]=[data[param].min().compute().values.tolist(),data[param].max().compute().values.tolist()]
    """
    vlims={}
    vlims['HTSGW_surface']=np.hstack([np.arange(0,1.6,.5),np.arange(2,15.1)])
    vlims['PERPW_surface']=np.hstack([np.arange(2,9,2),np.arange(9,21.1)])
    vlims['WIND_surface']=np.arange(4,69,4)
    vlims['WVHGT_surface']=vlims['HTSGW_surface']
    vlims['SWELL_surface']=vlims['HTSGW_surface']
    vlims['WVPER_surface']=vlims['PERPW_surface']
    vlims['SWPER_surface']=vlims['PERPW_surface']
    
    # for bug testing
    #regions={'global':{'name':'Global','lonlat':[0,360,-90,90],'crs':crs.Miller}}
    #cycles=range(0,4,6)
    
    # now do it one cycle at a time
    for cycle in cycles:    
        c00names=f'{dataDir}/{theDate:%Y%m%d}/nc/gefs.wave.t{cycle:02n}z.{dataTypes[0]}.global.0p25.f*.nc'
        ice=xr.open_mfdataset(c00names,decode_times=True)
        ice=ice['ICEC_surface'].where(ice['ICEC_surface']>0.15)
        fnames=f'{dataDir}/{theDate:%Y%m%d}/nc/gefs.wave.t{cycle:02n}z.{dataType}.global.0p25.f*.nc'
        data=xr.open_mfdataset(fnames,decode_times=True)
        data=xr.merge([data,ice])
        data.attrs['dataType']=dataType
        data.attrs['vDate']=theDate
        data['fcst']=(data.time.to_series()-data.time.to_series()[0])/60/60/1e9
        data['fcst']=data.fcst.astype('int')
        data=data.set_coords(['fcst'])
        data.attrs['cycle']=cycle
        data.attrs['vlims']=vlims
        
        if WantPool:
            for time in data.time:
                sel_data=data.sel(time=pd.Timestamp(time.values)).compute()
                with cf.ProcessPoolExecutor(maxjobs) as pool:
                    for name,region in regions.items():
                        pool.submit(plot_map,sel_data,region,params)
        else:
            for time in data.time:
                sel_data=data.sel(time=pd.Timestamp(time.values)).compute()
                for name,region in regions.items():
                    plot_map(sel_data,region,params)
                
