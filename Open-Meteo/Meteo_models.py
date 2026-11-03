from peewee import SqliteDatabase ,Model,FloatField,IntegerField,CharField,DateField

db = SqliteDatabase('weather_OM.db')

class Weather(Model):
    temp = FloatField()
    humidity = IntegerField()
    description = CharField(max_length=20)
    pressure = IntegerField()
    icon=CharField(max_length=20)
    city = CharField(max_length=20)
    date = DateField()
    
    class Meta:
        database = db 
        db_table = 'weather'
        
Weather.create_table()
    
    