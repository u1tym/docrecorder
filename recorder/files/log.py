# -*- coding: utf-8 -*-

import time
import datetime
import math

class LOG:

	def __init__( self, path, name ):

		if len( path ) == 0:
			path = "."

		self.path = path + "/" + name + ".log"

		self.f = open( self.path, mode='a', encoding='utf-8' )

	def output( self, level, message ):

		tm = time.time()
		tm_int = math.floor( tm )
		tm_mil = math.floor( tm * 1000 ) - tm_int * 1000
		dt = datetime.datetime.fromtimestamp( tm_int )
		dt_str = '{0:%Y-%m-%d %H:%M:%S}'.format( dt ) + '.' + str( tm_mil ).zfill( 3 )

#		print( dt_str + ' [' + level + '] ' + message )

		self.f.write( dt_str + ' [' + level + '] ' + message + '\n' )
		self.f.flush()

