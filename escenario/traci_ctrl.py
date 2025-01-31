import traci
import os
import sys
import json

import traci.constants

os.environ['SUMO_HOME'] = '/usr/share/sumo'
os.environ['LIBSUMO_AS_TRACI'] = '1'

sumocfg = {
    "use_gui" : True,
    "cfg" : "./osm2.sumocfg"
}

def close_traci():
    if traci.isLoaded():        
        traci.close()

if "SUDO_HOME" in os.environ:
    sys.path.append(os.path.join(os.environ["SUDO_HOME"], 'tools'))

sumo_cmd = 'sumo-gui' if sumocfg["use_gui"] else 'sumo'
sumo_cmd = [sumo_cmd, '-c', sumocfg["cfg"]]

if not traci.isLoaded():
    traci.start(sumo_cmd)

# semaforos
#tls = traci.trafficlight.getIDList()
# there is only one tl in this case (per intersection)
tl = traci.trafficlight.getIDList()[0]
sensors_induction = traci.inductionloop.getIDList()
sensors_lanearea = traci.lanearea.getIDList()

#for tl in tls:
traci.trafficlight.subscribe(tl,[traci.constants.TL_RED_YELLOW_GREEN_STATE, traci.constants.TL_CURRENT_PHASE, traci.constants.TL_NEXT_SWITCH])



for s in sensors_induction:
    traci.inductionloop.subscribe(s,[traci.constants.LAST_STEP_MEAN_SPEED])
for s in sensors_lanearea:
    traci.lanearea.subscribe(s,[traci.constants.LAST_STEP_MEAN_SPEED])



pprint = lambda s: print(json.dumps(s,indent=4))


def fetch_data():
    data = {}
    data_tls = traci.trafficlight.getSubscriptionResults(tl)
    if data_tls:
        #pprint(data_tls) 
        # state, phase, switch
        data['tls'] =  { tl: data_tls }
        for s in sensors_induction:
            data['E1'] = { s: traci.inductionloop.getSubscriptionResults(s)}
        for s in sensors_lanearea:
            data['E2'] = { s: traci.lanearea.getSubscriptionResults(s)}
        
        return data
    return None    


    #return json.dumps(filter_still(data,-1.0),indent=4)
    #return json.dumps(data,indent=4)
