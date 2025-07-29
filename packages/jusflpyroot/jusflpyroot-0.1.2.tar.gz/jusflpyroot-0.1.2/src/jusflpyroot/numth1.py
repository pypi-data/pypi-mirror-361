#!/usr/bin/env python3

import numpy as np
import ROOT
import click
import datetime as dt
from console import fg, bg
import gc # garbace collect on del
import os

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

    def print(self):
        """
        print kindof a table
        """
        print(f"{self.name:10s} '{self.title:35s}'  {str(self.tstamp)[:-3]}   {self.nbins}   ", end="")
        print(f"<{self.ledges.min()} - {self.redges.max()})   ", end="")
        print(f"[ {self.underflow} / {self.contents.sum()} / {self.overflow} ]  ", end="")
        print()

    @classmethod
    def list(cls):
        for ii in range(len(cls.instances)):
            i = cls.instances[ii]
            print(f"{ii:2d}. ", end="")
            i.print()

    @classmethod
    def from_th1(cls, hist: ROOT.TH1):
        """
        read existing TH1 and create a new object
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
        #I override
        obj.contents = np.array([hist.GetBinContent(i) for i in range(1, nbins + 1)])  #
        obj.centers = np.array([hist.GetBinCenter(i) for i in range(1, nbins + 1)])  #
        obj.ledges = np.array([hist.GetBinLowEdge(i) for i in range(1, nbins + 1)])  #
        obj.redges = obj.centers + (obj.centers - obj.ledges)
        obj.errors = np.array([hist.GetBinError(i) for i in range(1, nbins + 1)])
        #
        obj.uderflow = hist.GetBinContent(0)
        obj.overflow = hist.GetBinContent(nbins + 1)
        return obj

    @classmethod
    #def from_numpy_events(cls, events: np.ndarray, bin_edges: np.ndarray):
    def from_numpy_events(cls, events: np.ndarray, bins: int, rangex=None):
        """
        organize many events to a histogram
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
        obj = cls(bin_edges, contents, errors)
        obj.underflow = underflow
        obj.overflow = overflow
        obj.underflow_error = np.sqrt(underflow)
        obj.overflow_error = np.sqrt(overflow)
        return obj

    def to_th1(self):
        """
        return TH1 histo -  also needed for saving
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


    def save(self, filename: str, save_format: str = "numpy"):
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



    @classmethod
    def list_file(cls, filename: str):
        res = cls.get_names_ffile(filename)
        for i in res:
            print(f"f...   ...   {i}     (TH1 in {filename})")

    @classmethod
    def get_names_ffile(cls, filename: str): # ROOT ONLY
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


    @classmethod
    def load(cls, filename: str, name=None, load_format: str = "numpy"):
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
    h = ROOT.TH1F("namec", "histogram just here", 100, 0, 100)
    nh = NumpyTH1.from_th1(h)
    nh2 = NumpyTH1.load("bobes.root", "namea", load_format="root")

    print(" ... _______ I expect to see 'namec' (still in memory)   and 'namea' from disk")
    NumpyTH1.list()
    print(" ... _______ on disk:")
    NumpyTH1.list_file("bobes.root")
