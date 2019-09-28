import library

from datetime import datetime
config = library.init_config()
conn, client = library.init_mongodb_conn(config=config)

lt_time = (datetime.timestamp(datetime.utcnow()) - config.getint('system', 'max-idle-time', fallback=60))

rows = conn['online-users'].find({
    'disconnected_at': None,
    'last_active_at': {
        '$lt': lt_time
    }
})

for row in rows:
    print('UserID:', str(row['_id']), 'is now disconnected')
    conn['online-users'].update_one({
        '_id': row['_id']
    }, {
        '$set': {
            'disconnected_at': datetime.utcnow()
        }
    })