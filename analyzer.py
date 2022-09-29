from ROOT import TFile, TLorentzVector, TH1F
import os, itertools
import truth


def createHistoObject(num: int, title: str = None) -> TH1F:
    histogram1 = TH1F(f"Invariant Mass, t{num}", "", 100, 0, 500)
    histogram1.GetXaxis().SetTitle(title if title is not None else f"t{num} Invariant Mass from estimated jets (GeV / c^2)")
    histogram1.GetYaxis().SetTitle("Frequency")
    return histogram1

def sumVecs(vectors: list):
    if len(vectors) == 1:
        return vectors[0]
    total = vectors[0] + vectors[1]
    for i in vectors[2:]:
        total += i
    return total

def main():
    input_name = "./tag_1_delphes_events.root"

    tree = TFile(input_name, "read")

    histograms = {
        1: createHistoObject(1),
        2: createHistoObject(2),
    }

    epsilon_event_total, epsilon_top_1_total, epsilon_top_2_total, identifiable_quarks_total, both_quarks_identifiable_events_total = 0, 0, 0, 0, 0

    branch = tree.Delphes
    for index, entry in enumerate(branch):
        
        if entry.Jet_size == 6: # entry.Jet_size >= 4:
            jets = []
            for i in range(entry.Jet_size):
                jet = TLorentzVector()
                jet.SetPtEtaPhiM(entry.GetLeaf("Jet.PT").GetValue(i), entry.GetLeaf("Jet.Eta").GetValue(i), entry.GetLeaf("Jet.Phi").GetValue(i), entry.GetLeaf("Jet.Mass").GetValue(i))
                jets.append(jet)
            

            
            predicted = []

            combinations = list(itertools.combinations(jets, 2))
            for i in range(3, len(jets)):
                combinations += list(itertools.combinations(jets, i))
            
            
            for i in combinations:

                others = jets[:]
                for j in i:
                    others.remove(j)
                
                if predicted is None or len(predicted) == 0:
                    predicted += [i, others]
                elif (sumVecs(i).M() - 172.76)**2 + (sumVecs(others).M() - 172.76)**2 < (sumVecs(predicted[0]).M() - 172.76)**2 + (sumVecs(predicted[1]).M() - 172.76)**2:
                    predicted[0] = i
                    predicted[1] = others
            
            predicted.sort(key=lambda x: sumVecs(x).M())

            histograms[1].Fill(sumVecs(predicted[0]).M())
            histograms[2].Fill(sumVecs(predicted[1]).M())
            
            print(index)

            actual = truth.get_serielized(entry)

            e_top_1 = False
            e_top_1_t = None
            e_top_2 = False
            print("----------------------------")
            for i in jets:
                for j in actual:
                    t = []
                    for k in j:
                        print(f"Delta R: {i.DeltaR(k)}")
                        if i.DeltaR(k) < 0.4:
                            t.append(k)
                    if len(t) == 3:
                        identifiable_quarks_total += 1

                        if e_top_1:
                            e_top_1 = False
                            e_top_1_t = None
                            e_top_2 = True
                            both_quarks_identifiable_events_total += 1
                            print("BOOM")
                            break
                        else:
                            e_top_1_t = t
                        
                        e_top_1 = True
                    print()
   
            if e_top_1:
                for i in predicted:
                    for j in i:
                        num = 0
                        for k in e_top_1_t:
                            if j.DeltaR(k) < 0.4:
                                num += 1
                        if num == len(e_top_1_t):
                            epsilon_top_1_total += 1
                            break
            
            event_success = False
            if e_top_2:
                for i in predicted:
                    for j in i:
                        for k in actual:
                            num = 0
                            for l in k:
                                if j.DeltaR(l) < 0.4:
                                    num += 1
                                if num == len(k):
                                    if event_success:
                                        epsilon_event_total += 1
                                    epsilon_top_2_total += 1
                                    event_success = True
            
                        
            
            # if e_top_2:
            #     for i in predicted:
            #         for j in i:



            print(f"epsilon_event: {epsilon_event_total} / {both_quarks_identifiable_events_total} = {0 if not both_quarks_identifiable_events_total else round(100 * epsilon_event_total / (both_quarks_identifiable_events_total), 2)}%")
            print(f"epsilon_top_1: {epsilon_top_1_total} / {identifiable_quarks_total} = {round(100 * epsilon_top_1_total / (identifiable_quarks_total), 2)}%")
            print(f"epsilon_top_2: {epsilon_top_2_total} / {both_quarks_identifiable_events_total * 2} = {0 if not both_quarks_identifiable_events_total else round(100 * epsilon_top_2_total / (both_quarks_identifiable_events_total * 2), 2)}%")

            # exit() # debug
            
    
    if not os.path.exists(f"{os.getcwd()}/output"):
        os.makedirs(f"{os.getcwd()}/output")

    for i in histograms:
        histograms[i].SaveAs(f"output/t{i}.root")


if __name__ == "__main__":
    main()