# File: ventaxiaiot/sentinel_kinetic.py

from dataclasses import dataclass, field
import json
from typing import Any, List, Optional
from datetime import datetime

from ventaxiaiot.pending_request_tracker import PendingRequestTracker


@dataclass
class SentinelKinetic:
    # Metadata
    m: Optional[str] = None  # message type
    t: Optional[str] = None  # topic
    i: Optional[int] = None  # message ID
    
    # Core operational state
    ar_af: Optional[int] = None  # User Airflow mode: 1=low, 2=normal, 3=boost, 4=purge 
    ar_min: Optional[int] = None  # Boost duration
    ts: Optional[int] = None  # Device timestamp (UNIX)

    # Environmental sensors
    temp_indoor: Optional[float] = None
    temp_outdoor: Optional[float] = None
    humidity: Optional[float] = None

    # Config / network status
    netmode: Optional[str] = None
    wifi_signal: Optional[int] = None

    # Device flags / identifiers
    serial: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None

    # Raw message cache (for optional access)
    # last_update: datetime = field(default_factory=datetime.utcnow)
    # last_raw: Dict[str, Any] = field(default_factory=dict)  
    
    # Realtime status
    set_rtc: Optional[str] = None
    cm_af_sup: Optional[int] = None # supply air  flow
    cm_af_exh: Optional[int] = None # exhust  air  flow
    hand: Optional[int] = None

    # Airflow stages
    af1sup: Optional[int] = None
    af1exh: Optional[int] = None
    af2sup: Optional[int] = None
    af2exh: Optional[int] = None
    af3sup: Optional[int] = None
    af3exh: Optional[int] = None
    af4sup: Optional[int] = None
    af4exh: Optional[int] = None

    # Identification
    dname: Optional[str] = None
    svcpn: Optional[str] = None
    loc: Optional[str] = None

    # Airflow settings
    af_ls1: Optional[int] = None
    af_sw1: Optional[int] = None
    af_p1: Optional[int] = None
    af_p2: Optional[int] = None
    af_irh: Optional[int] = None
    af_enp: Optional[int] = None
    af_do: Optional[int] = None

    # Logic switches and timers
    ls1o: Optional[int] = None
    ls1d: Optional[int] = None
    sw1t: Optional[int] = None
    p1t: Optional[int] = None
    p2t: Optional[int] = None

    # Preset thresholds
    p1a_lo: Optional[int] = None
    p1a_hi: Optional[int] = None
    p1b_lo: Optional[int] = None
    p1b_hi: Optional[int] = None
    p1c_lo: Optional[int] = None
    p1c_hi: Optional[int] = None

    p2a_lo: Optional[int] = None
    p2a_hi: Optional[int] = None
    p2b_lo: Optional[int] = None
    p2b_hi: Optional[int] = None
    p2c_lo: Optional[int] = None
    p2c_hi: Optional[int] = None

    irh_sp: Optional[int] = None

    # Device mode and runtime
    m_ctl: Optional[int] = None
    m_afr: Optional[int] = None
    m_byp: Optional[int] = None
    by_ti: Optional[int] = None
    by_to: Optional[int] = None
    shrs: Optional[int] = None
    flife: Optional[int] = None

    # Settings & Flags
    btn_en: Optional[int] = None
    moda: Optional[int] = None
    ctry: Optional[int] = None
    cfgf: Optional[int] = None
    svci: Optional[int] = None

    # Relay flags
    rlf1: Optional[int] = None
    rlf2: Optional[int] = None
    rlf1sp: Optional[int] = None
    rlf2sp: Optional[int] = None
    
        # Firmware / Info
    swver: Optional[int] = None
    wfver: Optional[int] = None
    mser: Optional[int] = None
    rtc: Optional[str] = None
    su_ver: Optional[int] = None

    # Runtime & diagnostics
    runh: Optional[int] = None
    shrem: Optional[int] = None
    fhrem: Optional[int] = None
    bfit: Optional[int] = None
    fl_l: Optional[int] = None
    fl_r: Optional[int] = None

    # Airflow/Temp/Humidity Sensors
    exr_rh: Optional[int] = None
    itk_rh: Optional[int] = None
    exr_t: Optional[int] = None
    itk_t: Optional[int] = None
    sup_t: Optional[int] = None
    exh_t: Optional[int] = None
    exr_thm: Optional[int] = None
    itk_thm: Optional[int] = None
    exr_sen: Optional[int] = None
    itk_sen: Optional[int] = None
    exr_f: Optional[int] = None
    itk_f: Optional[int] = None
    exr_ft: Optional[int] = None
    itk_ft: Optional[int] = None
    exr_cp: Optional[int] = None
    itk_cp: Optional[int] = None

    sup_pwm: Optional[int] = None
    exh_pwm: Optional[int] = None
    sup_rpm: Optional[int] = None  # supply rpm
    exh_rpm: Optional[int] = None  # exhust rpm 

    # Control & status
    mstat: Optional[int] = None
    byp: Optional[int] = None
    mflags: Optional[int] = None
    mdl_afu: Optional[int] = None

    # Auto-settings
    as_af: Optional[int] = None  # User Airflow mode: 1=low, 2=normal, 3=boost, 4=purge  
    as_ts: Optional[str] = None
    as_rsec: Optional[int] = None 
    as_oa: Optional[int] = None
    as_os: Optional[int] = None

    # Power
    pwr: Optional[int] = None #Power as a %
    afr_m: Optional[int] = None
    afr_php: Optional[int] = None

    # Server
    svr_conn: Optional[int] = None
    svrerr: Optional[int] = None
    svrstat: Optional[int] = None
    cmsrc: Optional[int] = None

    # Mode names
    mn: List[Optional[str]] = field(default_factory=lambda: [None]*16)
    
    AIRFLOW_MODES = {
        "reset": 0, # This stops the current user requested airflow mode
        "normal": 2,
        "boost": 3,
        "purge": 4,
    }
    
    VALID_DURATIONS = {0,15, 30, 45, 60} # 0 is sent with "reset": 0 to stop the current user requested airflow mode

    def apply_payload(self, data: Any,tracker : PendingRequestTracker):
        """Initialize or update the instance with nested or flat payload, handling mn0–mn15."""
        try:
            # Step 0: If input is a raw JSON string, try to parse it
            if isinstance(data, str):
                data = json.loads(data)
                
            # Step 0.5: Handle response metadata and assign to self
            msg_id = data.get("i")
            if msg_id is not None:
                meta = tracker.pop(msg_id) 
                if meta:
                    print(f"✅ Matched metadata for msg_id {msg_id}: {meta}")
                    key = meta.get("cfgcmd")
                    value = data.get("r")
                    if key and value is not None:
                        # Clean up key (e.g., "netmode?" → "netmode")
                        clean_key = key.rstrip("?")
                        print(f"🔧 Setting attribute: {clean_key} = {value}")
                        setattr(self, clean_key, value)    
                        return  # ✅ Done — no need to process further
                

            # Step 1: Unwrap nested keys if present
            if isinstance(data, dict):
                flat_data = data.get('d') or data.get('r') or data
            else:
                raise ValueError(f"Unexpected data type: {type(data)}")
            
            # Step 2.1: Define fields to ignore (e.g., internal timestamps)
            IGNORED_FIELDS = {f"ts{i}" for i in range(1, 28)}
            IGNORED_FIELDS.update({
                "mlang", "diag", "ls", "sw", "ps1", "ps2", "dsav", "warn", "secpin",
                "byp_ept", "afmax", "afcnt", "f90", "brid"
            })    
        

            # Step 2: Extract mn0–mn15 into a list and assign to `mn`
            mn_list = [flat_data.get(f'mn{i}') for i in range(16)]
            if any(v is not None for v in mn_list):
                self.mn = mn_list

            # Step 3: Update all fields defined in the dataclass
            for key, value in flat_data.items():
                if key.startswith("mn") and key[2:].isdigit(): 
                    continue  # already handled
                if hasattr(self, key):
                    setattr(self, key, value)
                elif key not in IGNORED_FIELDS:
                    print(f"⚠️ Unknown field ignored: {key}")

        except Exception as e:
            print(f"❌ apply_payload failed: {e}")

    @property
    def extract_temp_c(self) -> Optional[float]:
        """Extract (indoor) temperature in Celsius."""
        return self.exr_t / 10 if self.exr_t is not None and self.exr_t > -1000 else None
      
    @property
    def outdoor_temp_c(self) -> Optional[float]:
        """Outdoor (external) temperature in Celsius."""
        return self.itk_t / 10 if self.itk_t is not None and self.itk_t > -1000 else None   

    @property
    def supply_temp_c(self) -> Optional[float]:
        """Supply air temperature in Celsius."""           
        # Check if there's another field for supply temp; if not, maybe None
        if self.sup_t is not None and self.sup_t != -1000:
            return self.sup_t / 10.0
        return None
    
    @property
    def summer_bypass_indoor_temp(self) -> Optional[float]:
        """Summer bypass indoor temperature in Celsius."""           
        # Check if there's another field for supply temp; if not, maybe None
        return self.by_ti / 10 if self.by_ti is not None and self.by_ti > -1000 else None    
    
    @property
    def summer_bypass_outdoor_tempmp_c(self) -> Optional[float]:
        """Summer bypass outdoor temperature in Celsius."""           
        return self.by_to / 10 if self.by_to is not None and self.by_to > -1000 else None  
       
    
    @property
    def get_user_airflow_mode(self) -> Optional[str]:
        """Translate airflow setting to a friendly label"""
        user_airflow_modes = {
            1: "Normal",
            2: "Low",
            3: "Boost",
            4: "Purge"
        }
        return user_airflow_modes.get(self.as_af) if self.as_af is not None else "Unknown" # type: ignore

    def __str__(self):
        return f"<VentAxiaDevice name={self.dname} airflow_mode={self.get_user_airflow_mode} supply={self.cm_af_sup} exhaust={self.cm_af_exh}>"
