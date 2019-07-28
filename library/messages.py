from datetime import datetime


def insert(conn=None, user='user', user_room=None, user_id=None, type='normal', color=None, msg=None):
   conn['messages'].insert_one({
      'user': user,
      'user_id': user_id,
      'user_room': user_room,
      'type': type,
      'color': color,
      'msg': msg,
      'created_at': datetime.utcnow()
   })


def get(conn=None, room=None, limit=50):
   return conn['messages'].find({
      'user_room': room
   }).sort([('created_at', -1)]).limit(limit)

