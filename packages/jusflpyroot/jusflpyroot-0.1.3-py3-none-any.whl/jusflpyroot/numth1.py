#!/usr/bin/env python3

import numpy as np
import ROOT
ROOT.gStyle.SetOptStat(1111111)
ROOT.gStyle.SetPadGridX(True)
ROOT.gStyle.SetPadGridY(True)
import click
import datetime as dt
from console import fg, bg
import gc # garbace collect on del
import os
import math
import threading
import time

from iminuit import cost,Minuit
from scipy.stats import chi2


class PrepareLSQFit:
    cx = np.array([])
    y = np.array([])
    dy = np.array([])
    model = "p1"

    def __init__(self, x, y, dy):
        """
        init the cost function, it will contain the DATA: x,y,dy
        """
        self.cx = np.array(x)
        self.y = np.array(y)
        #self.dy = np.array(dy) # if dy==0!
        mindy_nz = min([x  for x in dy if x != 0 ])
        self.dy = np.array([x if x != 0 else mindy_nz for x in dy])
        self.model = None

    def pol0(a):
        return np.like_zeroes(self.cx) + a
    def pol1(a,b):
        return a * self.cx + b
    def pol0(a):
        return a ** 2 * self.cx + b * self.cx + c

    def set_model(self, mname):
        self.model = mname

    def get_model_points(self, **pars):
        """
        This is called by LSQ,  self.model is DETERMINED earlier
        """
        if self.model == "p0" and (len(pars) == 1):
            res = self.pol0(**pars.values() )
        if self.model == "p1" and (len(pars) == 2):
            res = self.pol1(**pars.values() )
        if self.model == "p2" and (len(pars) == 2):
            res = self.pol2(**pars.values() )
        return res

    def XI2(self, model_points):
        res =  np.sum( (self.y - model_points) ** 2 / self.dy ** 2)
        print(res)
        return res

    # least-squares score function = sum of data residuals squared
    def P0(self, a):
        model_points = np.zeros_like(self.cx) + a
        print(a, model_points)
        return self.XI2(model_points)
    def P1(self, a, b):
        model_points = self.cx *  a + b
        return self.XI2(model_points)
    def P2(self, a, b, c):
        model_points = self.cx *self.cx * a + self.cx *b + c
        return self.XI2(model_points)

    def FIT(self, **pars):
        """
        apriori unknown number of parameters - *args or **kwargs?
        """
        print(f"FIT  {pars}")
        m = None
        if self.model == "p0" and (len(pars) == 1):
            m = Minuit(self.P0, **pars)
        if self.model == "p1" and (len(pars) == 2):
            m = Minuit(self.P1, **pars)
        if self.model == "p2" and (len(pars) == 2):
            m = Minuit(self.P2, **pars)
        #m = Minuit(self.LSQ, **pars_initial)
        print("---------------------------------------")
        res = m.migrad()

        print(res)

        if m.valid:
            print(f"FCN={m.fval} nfcn steps={m.nfcn} npar={m.npar} dpoints={len(self.cx)}  ndofNAN={m.ndof}")
            chi2_value = m.fval
            dof = len(self.cx)-m.npar
            percentile = self.chi2_percentile(chi2_value, dof)
            p_value = 1 - chi2.cdf(chi2_value, dof)
            #print(percentile)
            print(f"i... {fg.green}  ****   X^2/dof={chi2_value/dof:.3f}   ... Xi2 percentile= {percentile:.3f} {fg.default}  pvalue={p_value:.3f} (low p rejects)*****")
            # Example usage
            # chi2_value = your chi-square value
            # dof = degrees of freedom

            for i in m.parameters:
                #print(i)
                #print(str(i))
                print(f" {i}   {m.values[i]:.4f} +- {m.errors[i]:.4f}  ")
        else:
            print(f"{fg.red}X... invalid fit ............................{fg.default}")

    @staticmethod
    def chi2_percentile(chi2_value, dof):
        p_value = chi2.cdf(chi2_value, dof)
        return p_value


# ================================================================================
#
# --------------------------------------------------------------------------------

class NumpyTH1:
    instances = []  # class list to track objects

    def __init__(self, bin_edges: np.ndarray, contents: np.ndarray, errors: np.ndarray = None):
        NumpyTH1.instances.append(self)
        self.bin_edges = bin_edges
        #
        self.contents = contents
        self.edges = bin_edges
        self.centers =  0.5 * (self.edges[1:] + self.edges[:-1])
        #
        self.errors = errors if errors is not None else np.sqrt(contents)
        self.underflow = 0.0
        self.overflow = 0.0
        self.underflow_error = 0.0
        self.overflow_error = 0.0
        #
        self.name = "name_unknown"
        self.title = "title_unknown"
        self.tstamp = dt.datetime.now()
        self.nbins = 0


    def __str__(self):
        """
        print kindof a table - per object
        """
        res = ""
        res = res + f"{self.name:10s} '{self.title:35s}'  {str(self.tstamp)[:-3]}   {self.nbins:5}   "
        res = res +f"<{self.ledges.min()} - {self.redges.max()})   "
        res = res +f"[ {self.underflow} / {self.contents.sum()} / {self.overflow} ]  "
        return res

    def get_xy(self, position="center"):
        """
        get numpy vectors x and y  possible center | ledge | redge
        """
        if position.find("center") >= 0:
            return self.centers, self.contents, self.errors
        elif position.find("ledge") >= 0:
            return self.ledges, self.contents, self.errors
        elif position.find("redge") >= 0:
            return self.redges, self.contents, self.errors
        else:
            return None, None, None

    @classmethod
    def list(cls):
        """
        list local instances
        """
        for ii in range(len(cls.instances)):
            i = cls.instances[ii]
            print(f"{ii:2d}. ", end="")
            print(i)#.print()


    @classmethod
    def from_th1(cls, hist: ROOT.TH1):
        """
        read existing TH1 and create a new object ... seems to work ......
        """
        nbins = hist.GetNbinsX()
        edges = np.array([hist.GetBinLowEdge(i) for i in range(1, nbins + 2)]) # ????

        #  like return new instance/object  cls....
        full_contents = np.array([hist.GetBinContent(i) for i in range(0, nbins + 2)])  #
        errors = np.array([hist.GetBinError(i) for i in range(0, nbins + 2)])
        obj = cls(edges, full_contents[1:-1], errors[1:-1])
        obj.underflow = full_contents[0]
        obj.overflow = full_contents[-1]
        #obj.underflow_error = errors[0]
        #obj.overflow_error = errors[-1]
        #
        #   calcualte centerrs....
        # cx = 0.5 * (xe[1:] + xe[:-1])
        #    calculate edges....
        #dx = np.diff(cx)[0] # if uniform diff
        #xe = np.concatenate(([cx[0] - dx/2], cx + dx/2))

        obj.name = hist.GetName()
        obj.title = hist.GetTitle()
        obj.nbins = nbins
        #I override previous things
        obj.contents = np.array([hist.GetBinContent(i) for i in range(1, nbins + 1)])  #
        obj.centers = np.array([hist.GetBinCenter(i) for i in range(1, nbins + 1)])  #
        obj.ledges = np.array([hist.GetBinLowEdge(i) for i in range(1, nbins + 1)])  #
        obj.redges = obj.centers + (obj.centers - obj.ledges)
        #
        # h.Fill(i, i)  makes dY == Y !   ------------------ trick ------ against bad/special  filling --- carefully
        # for j in range(i): h.Fill(i) makes dY=sqrt(Y)
        obj.errors = np.array([hist.GetBinError(i) for i in range(1, nbins + 1)] )
        #obj.errors = np.array([hist.GetBinError(i) if (hist.GetBinError(i) != hist.GetBinContent(i)) else math.sqrt(hist.GetBinContent(i)) for i in range(1, nbins + 1)] )
        #
        obj.uderflow = hist.GetBinContent(0)
        obj.overflow = hist.GetBinContent(nbins + 1)
        return obj

    def Draw(self):
        """
        I must create a persistent object
        """
        self.local_th1 = self.to_th1()
        self.local_th1.Print()
        self.local_th1.Draw("HISTOE1")


    @classmethod
    #def from_numpy_events(cls, events: np.ndarray, bin_edges: np.ndarray):
    def from_numpy_events(cls, events: np.ndarray, bins: int, rangex=None):
        """
        organize many events to a histogram ???? ???? ????
        """
        myrange = rangex
        if myrange is None:
            myrange = (events.min(), events.max())
        #contents, _ = np.histogram(events, bins=bin_edges ) # ,range=xr (0,2)
        contents, bin_edges = np.histogram(events, bins=bins, rangex=myrange ) # ,range=xr (0,2)
        # For errors, use sqrt(contents) as default
        errors = np.sqrt(contents)
        underflow = np.sum(data < bin_edges[0]) # ???
        overflow = np.sum(data >= bin_edges[-1])
        #-----------------------------
        obj = cls(bin_edges, contents, errors)
        obj.underflow = underflow
        obj.overflow = overflow
        obj.underflow_error = np.sqrt(underflow)
        obj.overflow_error = np.sqrt(overflow)
        return obj

    def to_th1(self):
        """
        return TH1 histo -  also needed for saving ... seems to work
        """
        nbins = len(self.contents)
        hist = ROOT.TH1D(self.name, self.title, nbins, self.bin_edges[0], self.bin_edges[-1])
        for i in range(nbins):
            hist.SetBinContent(i + 1, self.contents[i])
            hist.SetBinError(i + 1, self.errors[i])
        hist.SetBinContent(0, self.underflow)
        hist.SetBinError(0, self.underflow_error)
        hist.SetBinContent(nbins + 1, self.overflow)
        hist.SetBinError(nbins + 1, self.overflow_error)
        return hist

    @classmethod
    def list_file(cls, filename: str):
        """
        show file content
        """
        res = cls.get_names_ffile(filename)
        for i in res:
            print(f"f...   ...   {i}     (TH1 in {filename})")

    @classmethod
    def get_names_ffile(cls, filename: str): # ROOT ONLY
        """
        get list of OBJ TH1
        """
        ok = False
        linames = []
        if not os.path.exists(filename):
            return linames
        try:
            root_file = ROOT.TFile(filename, "READ")
            keys = root_file.GetListOfKeys()
            ok = True
        except:
            print(f"{fg.red}X... file open failed: {fg.default} ", filename)
            pass
        if not ok:
            return linames
        hist = None
        cnt = 0
        for key in keys:
            #print(f" ...  ... ... ... {key} ")
            obj = key.ReadObj()
            if isinstance(obj, ROOT.TH1):
                linames.append(key.GetName())
                cnt += 1
        #print(f"i... there is {cnt} histograms in the file")
        return linames


    # ----saving, self.....
    def save(self, filename: str, save_format: str = "root"):
        """
        convert to_th1 and save
        """
        print(f"i...  saving   histo '{self.name}'  into   '{filename}' ")
        save_format = save_format.lower()
        if save_format == "numpy":
            np.savez(filename,
                     bin_edges=self.bin_edges,
                     contents=self.contents,
                     errors=self.errors,
                     underflow=self.underflow,
                     overflow=self.overflow,
                     underflow_error=self.underflow_error,
                     overflow_error=self.overflow_error)
        elif save_format == "root":
            ok = False
            linames = NumpyTH1.get_names_ffile(filename)
            #print(linames)
            if self.name in linames:
                print(f"{fg.red}X...                 '{self.name}'  already exists in {filename}   - NOT saved {fg.default}")
                return
            try:
                root_file = ROOT.TFile(filename, "UPDATE")
                keys = root_file.GetListOfKeys()
                #root_file = ROOT.TFile(filename, "RECREATE")
                hist = self.to_th1()
                hist.Write()
                root_file.Close()
                ok = True
            except:
                pass
            if not ok:
                print(f"{fg.red}X... file open/write failed: {fg.default}", filename)

        else:
            raise ValueError("Unsupported save_format. Use 'numpy' or 'root'.")




    # --------------------------------------------------------------------- LOAD
    @classmethod
    def load(cls, filename: str, name=None, load_format: str = "root"):
        """
        create on load
        """
        print(f"i...  loading        '{name}'    from {filename} ")
        load_format = load_format.lower()
        if load_format == "numpy":
            if not os.path.exists(filename):
                print('raise FileNotFoundError(f"{filename} not found")')
            data = np.load(filename)
            obj = cls(data['bin_edges'], data['contents'], data['errors'])
            obj.underflow = data['underflow'].item()
            obj.overflow = data['overflow'].item()
            obj.underflow_error = data['underflow_error'].item()
            obj.overflow_error = data['overflow_error'].item()
            return obj
        elif load_format == "root" and name is not None:
            ok = False
            try:
                root_file = ROOT.TFile(filename, "READ")
                keys = root_file.GetListOfKeys()
                ok = True
            except:
                print(f"{fg.red}X... file open failed: {fg.default}", filename)
                pass
            if not ok:
                return None
            hist = None
            cnt = 0
            for key in keys:
                #print(f" ...  ... {key} ")
                obj = key.ReadObj()
                if isinstance(obj, ROOT.TH1):
                    cnt += 1
            print(f"i... there is {cnt} histograms total in the file")
            for key in keys:
                obj = key.ReadObj()
                if isinstance(obj, ROOT.TH1) and name == obj.GetName():
                    hist = obj
                    break  # means loads the 1st???
            if hist is None:
                root_file.Close()
                print('raise ValueError("No TH1 histogram found in ROOT file  - with the desired name")')
                return None
            obj = cls.from_th1(hist)
            root_file.Close()
            return obj
        else:
            raise ValueError("Unsupported load_format. Use 'numpy' or 'root'.")

    # ------------------------- deleting -------------------------------------
    def force_del(self):
        #try:
        print(f"{fg.darkslateblue}D...  deleting histo '{self.name}'  #instances  {len(NumpyTH1.instances):2d} =>", end="")
        NumpyTH1.instances.remove(self)
        print(f"  {len(NumpyTH1.instances):2d}  {fg.default}", end="\n")
        del self
        gc.collect()
        #except ValueError:
        #    print(f"{fg.red}X... something went wrong when removing the histo from instances{fg.default}")
        #    pass

    def __del__(self):
        """
        not sure if useful
        """
        try:
            NumpyTH1.instances.remove(self)
        except ValueError:
            pass

    # ---------------------  special operations
    @staticmethod
    def wait_loop():
        while True:
            maxc = ROOT.gROOT.GetListOfCanvases().GetEntries()
            vis = 0
            for i in range(maxc):
                ci = ROOT.gROOT.GetListOfCanvases().At(i)
                if ci.GetCanvasImp(): vis += 1
                ci.Modified()
                ci.Update()
            if vis <= 0:   break
            time.sleep(1)



# **************************************************************************************************************************
if __name__ == "__main__":

    NumpyTH1.list_file("bobes.root") #  list the file content if exists
    #   create one ROOT  histogram
    h = ROOT.TH1F("namea", "histogram that goes to file", 100, 0, 100)

    print("i... filling-in with a binary pattern to distinguish under/ovrflow and the content")
    h.Fill(- 1 )            # underflow
    h.Fill(0, 2)            # 2x inside
    h.Fill(100 - 0.0001, 4) # 4x inside
    h.Fill(100 , 8)         # 8x overflow

    #   create THE OBJECT
    nh = NumpyTH1.from_th1(h)
    nh.save("bobes.root", save_format="root")
    nh.force_del()  # brutally remove the object from instances

    # once more, but empty, I dont care about 'h'
    h = ROOT.TH1F("nameb", "histogram that also goes to file", 100, 0, 100)
    nh = NumpyTH1.from_th1(h)
    nh.save("bobes.root", save_format="root")
    nh.force_del()

    # last time, but dont delete this time
    h = ROOT.TH1F("namec", "histogram just here", 10, 0, 10)
    for i in range(11):
        #h.Fill(i, i * i * 0.03 + i)
        for n in range(i * 10):
            h.Fill(i)
    for i in range(31):
        h.Fill(3)
    nh = NumpyTH1.from_th1(h)
    nh2 = NumpyTH1.load("bobes.root", "namea", load_format="root")

    print(" ... _______ I expect to see 'namec' (still in memory)   and 'namea' from disk")
    NumpyTH1.list()
    print(" ... _______ on disk:")
    NumpyTH1.list_file("bobes.root")
    x, y, dy = nh.get_xy()
    print(x)
    print(y)
    print(dy)

    A = PrepareLSQFit(x, y, dy )
    A.set_model("p1")
    A.FIT( a=1, b=1 )

    nh.Draw()

    NumpyTH1.wait_loop()

#     ROOT.gInterpreter.Declare('''
# void exec3event(Int_t event, Int_t x, Int_t y, TObject *selected){TCanvas *c = (TCanvas *)gTQSender;
#     cout<<event<<x<<y<< selected->IsA()->GetName()<<endl;;}
# ''')
#     #exec3event = ROOT.exec3event
# #    ROOT.gInterpreter.Declare('''
# #void exec3event(Int_t event, Int_t x, Int_t y, TObject *selected){TCanvas *c = (TCanvas *)gTQSender;
# #    printf("Canvas %s: event=%d, x=%d, y=%d, selected=%s\n", c->GetName(), event, x, y, selected->IsA()->GetName());}
# #''')
#     #exec3event = ROOT.exec3event( event: ctypes.c_int, x: ctypes.c_int, y: ctypes.c_int, selected: ROOT.TObject)
#     #def exec3event(event, x, y, selected):
#     #    c = ROOT.gTQSender
#     #    print(f"Canvas {c.GetName()}: event={event}, x={x}, y={y}, selected={selected.IsA().GetName()}")


#     ROOT.gROOT.GetListOfGlobalFunctions().Delete()
#     h = ROOT.TH1F("h", "h", 100, -3, 3)
#     h.FillRandom("gaus", 1000)
#     c1 = ROOT.TCanvas("c1")
#     h.Draw()
#     c1.Update()
#     #    c1.Connect("ProcessedEvent(Int_t,Int_t,Int_t,TObject*)", 0, 0, "exec3event(Int_t,Int_t,Int_t,TObject*)")

#     # Connect using the static method with sender, signal, receiver class, receiver, slot
#     #ROOT.TQObject.Connect(c1, "ProcessedEvent(Int_t,Int_t,Int_t,TObject*)", "", ROOT.nullptr,  ROOT.exec3event() )
#     c1.Connect(c1, "ProcessedEvent(Int_t,Int_t,Int_t,TObject*)", "", ROOT.nullptr,  ROOT.exec3event() )
#     ####ROOT.TQObject.Connect(c1, "", "", None, *exec3event  )
#     NumpyTH1.wait_loop()
