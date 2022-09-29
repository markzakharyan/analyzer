from ROOT import TFile, TLorentzVector, TH1F
import os

def __fr(id: int) -> str:
    ids = {24: "w", 6: "t", 1: "d", 2: "u", 3: "s", 4: "c", 5: "b"}

    if id is None: return None

    anti = True if id < 0 else False
    lookup = None
    if abs(id) in ids:
        lookup = ids[abs(id)]
        if anti: lookup = "-" + lookup
    return lookup if lookup is not None else id

def __fr_list(iters: list) -> list:
    out = []
    for id in iters:
        # if fr(id) is not float:
        #     out.append(fr(id))
        out.append(__fr(id))
    return out

def get_serielized(entry):

       
    pid = entry.GetLeaf("Particle.PID")

    ts = []
    ws = []
    
    serielized = []
    
    for i in range(pid.GetLen()):
        id = int(pid.GetValue(i))
        
        
        if abs(id) == 6:
            status = int(entry.GetLeaf("Particle.Status").GetValue(i))

            m1_index = int(entry.GetLeaf("Particle.M1").GetValue(i))
            m2_index = int(entry.GetLeaf("Particle.M2").GetValue(i))
            w_i = int(entry.GetLeaf("Particle.D1").GetValue(i))
            b_i = int(entry.GetLeaf("Particle.D2").GetValue(i))

            m1 = None if m1_index == -1 else int(entry.GetLeaf("Particle.PID").GetValue(m1_index))
            m2 = None if m2_index == -1 else int(entry.GetLeaf("Particle.PID").GetValue(m2_index))
            w = int(entry.GetLeaf("Particle.PID").GetValue(w_i))
            b = int(entry.GetLeaf("Particle.PID").GetValue(b_i))
            
            t = TLorentzVector()
            t.SetPtEtaPhiM(entry.GetLeaf("Particle.PT").GetValue(i), entry.GetLeaf("Particle.Eta").GetValue(i), entry.GetLeaf("Particle.Phi").GetValue(i), entry.GetLeaf("Particle.Mass").GetValue(i))



            if status == 62:
                jet1_i = int(entry.GetLeaf("Particle.D1").GetValue(b_i))
                jet2_i = int(entry.GetLeaf("Particle.D2").GetValue(b_i))

                jet1_status = int(entry.GetLeaf("Particle.Status").GetValue(jet1_i))
                jet2_status = int(entry.GetLeaf("Particle.Status").GetValue(jet2_i))

                jet1 = int(entry.GetLeaf("Particle.PID").GetValue(jet1_i))
                jet2 = int(entry.GetLeaf("Particle.PID").GetValue(jet2_i))

                # print(f"p: {__fr(id)}, id: {id}, mo1_id: {m1}, mo2_id: {m2}, mo1: {__fr(m1)}, mo2: {__fr(m2)}, d1: {__fr(w)}, d2: {__fr(b)}, d2_d1: {__fr(jet1)}, d2_d2: {__fr(jet2)}, status: {status}") # DEBUG
                
                w = TLorentzVector()
                w.SetPtEtaPhiM(entry.GetLeaf("Particle.PT").GetValue(w_i), entry.GetLeaf("Particle.Eta").GetValue(w_i), entry.GetLeaf("Particle.Phi").GetValue(w_i), entry.GetLeaf("Particle.Mass").GetValue(w_i))
                
                j1 = TLorentzVector()
                j1.SetPtEtaPhiM(entry.GetLeaf("Particle.PT").GetValue(jet1_i), entry.GetLeaf("Particle.Eta").GetValue(jet1_i), entry.GetLeaf("Particle.Phi").GetValue(jet1_i), entry.GetLeaf("Particle.Mass").GetValue(jet1_i))

                j2 = TLorentzVector()
                j2.SetPtEtaPhiM(entry.GetLeaf("Particle.PT").GetValue(jet2_i), entry.GetLeaf("Particle.Eta").GetValue(jet2_i), entry.GetLeaf("Particle.Phi").GetValue(jet2_i), entry.GetLeaf("Particle.Mass").GetValue(jet2_i))

                b = TLorentzVector()
                b.SetPtEtaPhiM(entry.GetLeaf("Particle.PT").GetValue(b_i), entry.GetLeaf("Particle.Eta").GetValue(b_i), entry.GetLeaf("Particle.Phi").GetValue(b_i), entry.GetLeaf("Particle.Mass").GetValue(b_i))

                ts.append(t)
                ws.append(w)
                instance = [j1, j2, b]
                serielized.append(instance)

    return serielized
