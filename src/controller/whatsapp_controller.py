from model import *
class WhatsApp:
    def __init__(self):
        pass

    def management_view_whatsapp():
        data = model.ManagementStorage.check_whatsapp() # -> [1 2 3 4 5]
        view = view_whatsapp()
        
        for i in range(20):
            view.table(column=a, row=b, data[i])
        pass