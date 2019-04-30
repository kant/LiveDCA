import Live
import re


# constant definitions
NORMAL = 1
RETURN = 2
MASTER = 3

UPDATE_TIME = 5



# Main class

class LiveDCA:
    __module__ = __name__
    __doc__ = "Main class that establishes the DCA processing"
    

    def __init__(self, c_instance):
        self._DCA__c_instance = c_instance
        self._Application_ = Live.Application.get_application()
        self.doc = self._DCA__c_instance.song()
        
        print ("initializing")
        
        # dictionnary that references the parameter changes for the DCA masters
        self.DCA_Modifs_dict = {}   # {(DCA_key, param_change) : DCA_track }
        
        # dictionnary/ list that references the DCA Masters
        self.DCA_Masters_dict = {}  # {track : DCA_track}
        self.DCA_Masters_list = []  # List of DCA_track objects
    
        
        self.major_version = self._Application_.get_major_version()
        self.minor_version = self._Application_.get_minor_version()
        print ("Live version : %d.%d" % (self.major_version, self.minor_version))

        # Function that builds the DCA list and initialize the DCA processing
        self.create_DCA_Masters_list()
        
        if self.major_version > 9 or (self.major_version == 9 and self.minor_version >= 5) :
            # Create the timer that periodicaly updates slaves parameters
            self.timer = Live.Base.Timer(self.update_slaves, UPDATE_TIME, repeat = True, start = True)
        
        print("DCA script initialized")

        
    
    
    def update_display(self):
        """
        This function is run every 100ms, it is this function that takes on the updates of the slaves parameters.
        """
        self.update_slaves()





    def update_slaves(self):
        
        while self.DCA_Modifs_dict != {} :
            entry = self.DCA_Modifs_dict.popitem()
            key_param = entry[0]
            param_change = key_param[1]
            key = key_param[0]
            master_track = entry[1]
                 
                  
            # remove listeners to avoid looping
            listener_dict = {}      
            for dca in self.DCA_Masters_list : 
                if dca.key == key :
                    listener_dict[dca] = dca.remove_listener(param_change)
                    
                    
            # update tracks values
            master_track.update_slaves_parameters(param_change)
            
            # add listeners back
            while listener_dict != {} :
                entry = listener_dict.popitem()
                dca = entry[0]
                dca.update_parameter(param_change)
                listener = entry[1]
                dca.add_listener(param_change, listener)
         
        
        
        
            
            
    # Create Tracks dictionaries
    def create_DCA_Masters_list(self):
        print("creating dca list")
        doc = self.doc
        
        # create tracks listeners
        if not doc.tracks_has_listener(self.create_DCA_Masters_list) :
            doc.add_tracks_listener(self.create_DCA_Masters_list)
        if not doc.return_tracks_has_listener(self.create_DCA_Masters_list) :
            doc.add_return_tracks_listener(self.create_DCA_Masters_list)
            
        

        # create track names listeners
        for track in list(doc.tracks + doc.return_tracks) :
            if not track.name_has_listener(self.create_DCA_Masters_list) :
                track.add_name_listener(self.create_DCA_Masters_list)
               
        
        # empty DCA_Masters_dict    
        for dca in self.DCA_Masters_list :
            dca.destruct()
        del self.DCA_Masters_list[:]
            

        for master_track in self.doc.tracks :
        
            # create master          
            DCA_Master = DCA_track(master_track, NORMAL)
            
            # look for slaves
            for track in doc.tracks :
                if DCA_Master.is_master(track):
                    DCA_Master.add_slave(track,NORMAL, self.DCA_Modifs_dict)

            for track in doc.return_tracks :
                if DCA_Master.is_master(track):
                    DCA_Master.add_slave(track,RETURN, self.DCA_Modifs_dict)
        
            track = doc.master_track
            if DCA_Master.is_master(track):
                DCA_Master.add_slave(track,MASTER, self.DCA_Modifs_dict)
                          
            if DCA_Master.has_slaves() :
                # add entry in DCA_Masters_dict
                self.DCA_Masters_dict[DCA_Master.track] = DCA_Master
                self.DCA_Masters_list.append(DCA_Master)
                
                
        for master_track in self.doc.return_tracks :
            # create master          
            DCA_Master = DCA_track(master_track, RETURN)
            
            # look for slaves         
            for track in doc.tracks :
                if DCA_Master.is_master(track):
                    DCA_Master.add_slave(track,NORMAL, self.DCA_Modifs_dict)

            for track in doc.return_tracks :
                if DCA_Master.is_master(track):
                    DCA_Master.add_slave(track,RETURN, self.DCA_Modifs_dict)
        
            track = doc.master_track
            if DCA_Master.is_master(track):
                DCA_Master.add_slave(track,MASTER, self.DCA_Modifs_dict)
              
            if DCA_Master.has_slaves() :
                # add entry in DCA_Masters_dict
                self.DCA_Masters_dict[DCA_Master.track] = DCA_Master
                self.DCA_Masters_list.append(DCA_Master)
                    
                    
        master_track = self.doc.master_track
        # create master          
        DCA_Master = DCA_track(master_track, MASTER)
            
        # look for slaves
        for track in doc.tracks :
            if DCA_Master.is_master(track):
                DCA_Master.add_slave(track,NORMAL, self.DCA_Modifs_dict)

        for track in doc.return_tracks :
            if DCA_Master.is_master(track):
                DCA_Master.add_slave(track,RETURN, self.DCA_Modifs_dict)     
        
        if DCA_Master.has_slaves() :
            # add entry in DCA_Masters_dict
            self.DCA_Masters_dict[DCA_Master.track] = DCA_Master
            self.DCA_Masters_list.append(DCA_Master)
                
        for dca in self.DCA_Masters_list :
            print("DCA : " + str(dca.name))
            


    #############################################################################################
    # Standard Ableton Methods

    def connect_script_instances(self, instanciated_scripts):
        """
        Called by the Application as soon as all scripts are initialized.
        You can connect yourself to other running scripts here, as we do it
        connect the extension modules
        """
        return

    def is_extension(self):
        return False

    def request_rebuild_midi_map(self):
        """
        To be called from any components, as soon as their internal state changed in a 
        way, that we do need to remap the mappings that are processed directly by the 
        Live engine.
        Dont assume that the request will immediately result in a call to
        your build_midi_map function. For performance reasons this is only
        called once per GUI frame.
        """
        return self.create_DCA_Masters_list()


    
    def disconnect(self):
        return

    def build_midi_map(self, midi_map_handle) :
        self.refresh_state()            
            
    def refresh_state(self):
        pass
       
    def send_midi(self, midi_event_bytes):
        """
        Use this function to send MIDI events through Live to the _real_ MIDI devices 
        that this script is assigned to.
        """
        pass
    
    def receive_midi(self, midi_bytes):
        return

    def can_lock_to_devices(self):
        return False

    def suggest_input_port(self):
        return ''

    def suggest_output_port(self):
        return ''

    def __handle_display_switch_ids(self, switch_id, value):
        pass
    
    



###############################################################
    
###############################################################
    


class DCA_track:
    # Class that describes a DCA Master, its parameters and slaves

    def __init__(self, track, track_type) :
        self.name = track.name    
        self.track = track   
        self.key = track.name.partition('/')[0].partition(' -')[0].lstrip().rstrip()      # the key is the name of the DCA group
        
        self.master_params = self.parse_arguments(self.name, track_type)    #dict{param : direction(1 or -1 for reverse)}
        
        self.slaves_params = {}
        for param in self.master_params :
            self.slaves_params[param] = {}
            
        self.slaves_params_dict = {}
        for param in self.master_params :
            self.slaves_params_dict[param] = []
       
            
        self.slaves_offsets = {}
        for param in self.master_params :
            self.slaves_offsets[param] = {}
        
            
        self.former_state = {}
        for param in self.slaves_params :
            if param in ("arm", "mute", "solo") :
                self.former_state[param] = eval("track." + param)
            else :
                self.former_state[param] = eval("track." + param + ".value")

        self.listeners = {}


    # parameter listener generator
    def master_parameter_listener (self, param, DCA_Modifs_dict) :
        key = self.key
        def listener_function() : 
            if (key, param) not in DCA_Modifs_dict :
                modif_key = (key, param)
                DCA_Modifs_dict[modif_key] = self
        return listener_function
            
            
            
            
    def destruct(self):
        # remove listeners
        for param in self.slaves_params :
            listener = self.listeners[param]
            self.remove_listener(param)
            
             
            
    def remove_listener(self, param) :
        if param in self.listeners :
            listener = self.listeners.pop(param)
            if param in ("arm", "mute", "solo") :
                 eval ("self.track.remove_" + param +"_listener(listener)")
            else :       
                eval ("self.track." + param +".remove_value_listener(listener)")
            return listener
        else :
            return None
    
    
    def add_listener (self, param, listener = 0) :
        if not self.listeners.has_key(param):
            if listener == 0 :
                listener = self.master_parameter_listener (param, DCA_Modifs_dict)
            self.listeners[param] = listener
            if param in ("arm", "mute", "solo") :
                eval ("self.track.add_" + param +"_listener(listener)")
            else : 
                eval ("self.track." + param + ".add_value_listener(listener)")
            self.listeners[param] = listener
                
                
    
    def parse_arguments(self, track_name, track_type) :
        namelist = track_name.split('/')
        args = 0
        # search keyname
        for s in namelist :
            s = s.lstrip()
            if s.startswith(self.key) :
                args = {"mixer_device.volume" : 1, "mixer_device.panning" : 1, "mute" : 1, "arm" : 1, "solo" : 1 }
                index = 0
                for send in self.track.mixer_device.sends :
                    exec( 'args["mixer_device.sends[' + str(index) + ']"] = 1' )
                    index += 1
                break
            elif s.startswith('@' + self.key) :
                args = {"mixer_device.volume" : 0, "mixer_device.panning" : 0, "mute" : 0, "arm" : 0, "solo" : 0 }
                index = 0
                for send in self.track.mixer_device.sends :
                    exec( 'args["mixer_device.sends[' + str(index) + ']"] = 0' )
                    index += 1
                break
        
        if args == 0 :
            return {}
        
        
        # search arguments
        s = s.partition(self.key)[2]
        
        if re.search(r"-[lL]\b", s) :
            args["mixer_device.panning"] = 1
            
        if re.search(r"-[rR]\b", s) :
            args["mixer_device.panning"] = -1
        
        
        
        args_list = re.findall(r"-([i-]?)([vpmaS]\b)", s)
        
        for arg in args_list :
            if arg[0] == "" :
                direction = 1
            elif arg[0] == "-" :
                direction = 0
            elif arg[0] == "i" :
                direction = -1
                
            if arg[1] == "v" :
                param = "mixer_device.volume"
            elif arg[1] == "p" :
                param = "mixer_device.panning"
            elif arg[1] == "m" :
                param = "mute"
            elif arg[1] == "a" :
                param = "arm"
            elif arg[1] == "S" :
                param = "solo"
        
            args[param] = direction
        
        # search sends arguments        
        args_list = re.findall(r"-([i-]?)s([A-L])?\b", s)
              
        for arg in args_list :
            if arg[0] == "" :
                direction = 1
            elif arg[0] == "-" :
                direction = 0
            elif arg[0] == "i" :
                direction = -1
          
            if arg[1] == "" :
                index = 0
                for send in self.track.mixer_device.sends :
                    exec ('args["mixer_device.sends[' + str(index) +']"] = direction')
                    index += 1
            else :
                exec ('args["mixer_device.sends[' + str(ord(arg[1]) - ord("A")) + ']"] = direction')
        
        if track_type == RETURN :
            if "arm" in args :
                args.pop("arm")
        elif track_type == MASTER :
            if "mute" in args :
                args.pop("mute")
            if "solo" in args :
                args.pop("solo")
            if "arm" in args :
                args.pop("arm")
            for index in range(12) :
                send_index = "mixer_device.sends[" + str(index) + "]"
                if send_index in args :
                    args.pop(send_index)
            
        return args
    
                    
                    
                    

    def add_slave (self, track, track_type, DCA_Modifs_dict) :
        # process slaves parameters 
        params = self.parse_arguments(track.name, track_type)
        
        while params != {} :
            entry = params.popitem()
            current_param = entry[0]
            direction = entry[1]
            if current_param in self.slaves_params and direction != 0 :
                # add slave_parameter to dict
                self.slaves_params_dict[current_param].append(Slave_Parameter(track, current_param, direction))
                # add slave to dict
                self.slaves_params[current_param][track] = direction
                # add offset entry
                self.slaves_offsets[current_param][track] = 0
        
                 # add listener
                if not self.listeners.has_key(current_param):
                    listener = self.master_parameter_listener (current_param, DCA_Modifs_dict)
                    self.listeners[current_param] = listener
                    if current_param in ("arm", "mute", "solo") :
                        eval ("self.track.add_" + current_param +"_listener(listener)")
                    else : 
                        eval ("self.track." + current_param + ".add_value_listener(listener)")
               
             
        

    def is_master(self, track) :
        if self.track == track :
            return False
        for key in track.name.split('/') :
            if self.key in key :
                return True
        return False
    
            
        
    def has_slaves (self) :
        return self.listeners != {} 
    
    
    
    def update_parameter(self, param_change) :
        if param_change in ("arm", "mute", "solo") :
            self.former_state[param_change] = eval("self.track." + param_change)
        else :
            self.former_state[param_change] = eval("self.track." + param_change + ".value")
            
            
    
    
    def update_slaves_parameters(self, param_change) :
        master_direction = self.master_params[param_change]
            
        if param_change in ("arm", "mute", "solo") :
            if master_direction != 0 :
                value = eval("self.track." + param_change)
                if master_direction == -1 :
                    value = not value
                    
                for slave_param in self.slaves_params_dict[param_change] :
                    slave_param.update_slave_parameter(value)
        
        else :
            param = eval("self.track." + param_change)
            delta = master_direction * (param.value - self.former_state[param_change])
            exec("self.former_state['" + param_change + "'] = self.track." + param_change + ".value")
            
            for slave_param in self.slaves_params_dict[param_change] :
                slave_param.update_slave_parameter(delta)


#######################################################################################
#######################################################################################


class Slave_Parameter :
    
    def __init__(self, track, param, direction) :
        self.track = track
        self.direction = direction
        
        if param in ("mute", "arm", "solo") :
            self.isFloat = False
        else :
            self.isFloat = True
            self.offset = 0
        self.param = eval ("track." + param)
        
        
    def update_slave_parameter(self, master_delta) :
        
        if self.isFloat :
            slave_delta = master_delta * self.direction
            
            if self.param.value == self.param.min :
                if self.param.value + self.offset + slave_delta < self.param.min :
                    self.offset += slave_delta
                else :
                    self.param.value += (self.offset + slave_delta)
                    self.offset = 0
                        
            elif self.param.value == self.param.max :
                if self.param.value + self.offset + slave_delta > self.param.max :
                    self.offset += slave_delta
                else :
                    self.param.value += (self.offset + slave_delta)
                    self.offset = 0
                        
            else :                
                if self.param.value + slave_delta < self.param.min :
                    self.offset = self.param.value + slave_delta - self.param.min
                    self.param.value = self.param.min
                elif self.param.value + slave_delta > self.param.max :
                    self.offset = self.param.value + slave_delta - self.param.max
                    self.param.value = self.param.max
                else :
                    self.param.value += slave_delta
                    self.offset = 0
                    
                    
        else :
            if self.direction == 1 :
                self.param = master_delta
            else :
                self.param = not master_delta
  