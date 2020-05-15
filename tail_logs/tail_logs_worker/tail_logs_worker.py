#!/usr/bin/env python3
#
# 2020-05-09, wildi.markus@bluewin.ch
#
#
'''

   
'''
__author__ = 'wildi.markus@bluewin.ch'

import os
import io
import sys
import argparse
import logging
import platform
import tailer
import os
import math
import re
import datetime as dt
import astropy.units as u
from astropy.coordinates import SkyCoord, ITRS, EarthLocation, Angle, AltAz
from astropy.time import Time
# workaround
from astropy.utils import iers
iers.Conf.iers_auto_url.set('ftp://cddis.gsfc.nasa.gov/pub/products/iers/finals2000A.all')


class Tail_logs_worker():
    terminate = False
    def __init__(self, lg = None, args = None, fn = None):
        self.lg=lg
        self.args = args
        self.fn = fn
        
        self.omega_sid = 2. *  math.pi / 86164.2 ;

    def tail(self):
        self.lg.debug(f'{self.fn}')
        if os.path.isdir(self.fn):
            self.lg.debug(f'is a directory : {self.fn}')
            return
        
        two_entries = 0
        lns = list()
        for ln in tailer.follow(open(self.fn)):
            self.lg.debug(''.join('%-7s' % item for item in ln.split('\t')))

            if '+++++++++++++' in ln:
                continue

            elif 'J2mnt_chr RA' in ln:
                two_entries += 1
                
            lns.append(ln)
            
            if two_entries == 2:
                self.analyze(lns = lns)
                two_entries = 0
                lns = list()
                
    def analyze(self, lns = None):
        
        first = True
        for ln in lns:
            if first:
                # DEBUG   389.935520 sec  : UTC            : 2020-03-22T14:31:49
                m = re.search(r'.+: UTC.+?: (.+)', ln)
                if m:
                    tz_start = m.group(1)

                # 2020-03-16T16:17:03: Driver ./indi_simulator_ccd: Longitude      : -123.350, Latitude    :  -75.100
                m = re.search(r'.+?Longitude.+?:[ ]+?([+-]?\d+\.\d*).*?([+-]?\d+\.\d*)', ln)
                if m:
                    obs_longitude = float(m.group(1))
                    obs_latitude = float(m.group(2))

                # 2020-03-16T16:17:03: Driver ./indi_simulator_ccd: mod ra         :  179.881,          dec:  -89.788 (degree)
                m = re.search(r'.+?:.+?mod ra.+?:[ ]+?([+-]?\d+\.\d*).*?([+-]?\d+\.\d*)', ln)
                if m:
                    ra0 =    float(m.group(1))  
                    dec0 =   float(m.group(2))
                    
                # measurement star ra
                # 2020-03-16T16:17:03: Driver ./indi_simulator_ccd: tel RA         :  295.612, Dec         :  -90.000
                m = re.search(r'.+?:.+?Jnow RA.+?:[ ]+?([+-]?\d+\.\d*).*?([+-]?\d+\.\d*)', ln)
                if m:
                    cntr_ra = m.group(1)
                    cntr_dec = m.group(2)

                # 2020-03-18T15:44:21: Driver ./indi_simulator_ccd: Jnow                               JnHA:   88.345 degree
                m = re.search(r'.+?:.+?Jnow.+?JnHA.*?([+-]?\d+\.\d*)', ln)
                if m:
                    m_tau = m.group(1)
                if 'J2mnt_chr RA' in ln:
                    first = False
            else:
                # DEBUG   389.935520 sec  : UTC            : 2020-03-22T14:31:49
                m = re.search(r'.+: UTC.+?: (.+)', ln)
                if m:
                    tz_end = m.group(1)

                # DEBUG   113.898934 sec  : mod ra         :   67.684,          dec:   88.080 (degree)
                m = re.search(r'.+?:.+?mod ra.+?:[ ]+?([+-]?\d+\.\d*).*?([+-]?\d+\.\d*)', ln)
                if m:
                    ra1 =    float(m.group(1))  
                    dec1 =   float(m.group(2))  

        self.lg.debug('tz_start: {}'.format(tz_start))
        self.lg.debug('tz_end: {}'.format(tz_end))
        self.lg.debug('obs_longitude: {}'.format(obs_longitude))
        self.lg.debug('obs_latitude: {}'.format(obs_latitude))
        self.lg.debug('cntr_ra: {}'.format(cntr_ra))
        self.lg.debug('cntr_dec: {}'.format(cntr_dec))
        self.lg.debug('m_tau: {}'.format(m_tau))
        self.lg.debug('ra0: {}'.format(ra0))
        self.lg.debug('dec0: {}'.format(dec0))
        self.lg.debug('ra1: {}'.format(ra1))
        self.lg.debug('dec1: {}'.format(dec1))
        
        t_start = dt.datetime.strptime(tz_start, '%Y-%m-%dT%H:%M:%S')
        t_end = dt.datetime.strptime(tz_end, '%Y-%m-%dT%H:%M:%S')
        t_diff = t_end - t_start
        cntr = SkyCoord(cntr_ra, cntr_dec, unit='deg', frame='icrs')
        loc = EarthLocation(lon=obs_longitude*u.deg, lat=obs_latitude*u.deg, height=0*u.m)
        t = Time(t_start, scale='utc', location=loc)
        local_ha = Angle(t.sidereal_time('apparent').radian - cntr.ra.radian, unit=u.radian)
        local_ha.wrap_at('180d', inplace=True)

        dec = Angle((dec1 + dec0)/2., unit = u.degree)
        d_ra = Angle(ra1 - ra0, unit = u.degree)
        
        dY =  Angle(d_ra.radian *  math.cos(dec.radian), unit = u.radian)
        dX =  Angle((dec1 - dec0), unit = u.degree)

        d_tau = Angle(self.omega_sid * t_diff.total_seconds(), unit = u.radian)
        d_ha = Angle(-math.atan2( -dX.radian, -dY.radian) * math.sin(dec.radian), unit = u.radian)
        mnt_ha = Angle(d_ha.radian + d_tau.radian/2. + local_ha.radian, unit = u.radian)

        mnt_gamma = Angle(math.sqrt(dX.radian**2 + dY.radian**2) / d_tau.radian, unit = u.radian)
        mnt_dec = Angle(math.pi/2. - mnt_gamma.radian, unit = u.radian)
        
        mnt = SkyCoord(mnt_ha, mnt_dec, unit= u.radian, frame='gcrs') # gcrs close to JNow
        loc_aa = AltAz(location=loc, obstime=t) 
        mnt_aa = mnt.transform_to(loc_aa)

        self.lg.info('center   RA: {},     dec: {}, HA: {}, decimal: {}'.format(cntr.ra.to_string(pad = True, precision = 1, alwayssign = True,  unit=u.hourangle, sep=':'),cntr.dec.to_string(pad = True, precision = 1, alwayssign = True, unit=u.degree, sep=':'), local_ha.to_string(pad = True, precision = 1, alwayssign = True, unit=u.hourangle, sep=':'), local_ha.degree)) 
        self.lg.info('mount gamma: {}, decimal: {}'.format(mnt_gamma.to_string(pad = True, precision = 1, alwayssign = True,  unit=u.degree, sep=':'), mnt_gamma.degree))
        self.lg.info('mount    HA: {},     dec: {}'.format(mnt.ra.to_string(pad = True, precision = 1, alwayssign = True,  unit=u.hourangle, sep=':'),mnt.dec.to_string(pad = True, precision = 1, alwayssign = True,  unit=u.degree, sep=':'))) # ra: misused
        self.lg.info('mount    Az: {},     Alt: {}'.format(mnt_aa.az.to_string(pad = True, precision = 1, alwayssign = True,  unit=u.hourangle, sep=':'),mnt_aa.alt.to_string(pad = True, precision = 1, alwayssign = True,  unit=u.degree, sep=':'))) 



if __name__ == "__main__":
    
    import tail_logs_worker as tlw
    import tail_logs_cli_args as cli
    
    tl = tlw.Tail_logs_worker(lg = cli.logger, args= cli.args, fn = cli.args.base_path)
    tl.tail()
