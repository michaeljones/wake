

sqlite3 $PIPELINE/db/pipeline.db .dump

if ( -e ~/.last.bck ) then
	mv ~/.last.bck ~/.last
endif 


