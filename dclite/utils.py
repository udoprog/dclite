def format_float(ss):
  return "%.2f"%(ss)

def format_bytes(ss):
  ss = float(ss);
  
  if ss >= 1024:
    ss = ss / 1024;
  else:
    return format_float(ss) + " B";
  
  if ss >= 1024:
    ss = ss / 1024;
  else:
    return format_float(ss) + " KiB";
  
  if ss >= 1024:
    ss = ss / 1024;
  else:
    return format_float(ss) + " MiB";
  
  if ss >= 1024:
    ss = ss / 1024;
  else:
    return format_float(ss) + " GiB";
  
  if ss >= 1024:
    ss = ss / 1024;
  else:
    return format_float(ss) + " TiB";
  
  return format_float(ss) + " PiB";

def format_bandwidth(ss):
  return format_bytes(ss) + "/s";
