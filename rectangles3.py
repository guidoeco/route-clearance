#!/usr/bin/env python

import argparse
from os import walk, path
import csv
import json
import numpy as np
from io import StringIO
import re
import pandas as pd
import hashlib

parser = argparse.ArgumentParser(description='Create ELR route clearance report')
parser.add_argument('route', type=str, nargs='?', default='Anglia', help='route directory')
parser.add_argument('--all', type=bool, nargs='?', default=True, help='process all route directories')

args = parser.parse_args()
route = path.dirname(args.route)
if route == '':
    route = args.route

def isin(text_str, this_path, ignorecase=False):
    this_text = text_str
    if ignorecase:
        this_text = this_text.lower()
    with open(this_path, 'r') as fin:
        for line in fin:
            line = line.strip()
            if ignorecase:
                line = line.lower()
            if this_text in line:
                return this_path

def get_files(text_str, this_path, key_str, ignorecase=False):
    file_array = []
    for (dirname, dirnames, filenames) in walk(this_path):
        for filename in filenames:
            if key_str not in filename: continue
            this_path = dirname + '/' + filename
            if text_str:
                this_path = isin(text_str, this_path, ignorecase)
            if this_path:
                file_array.append(this_path)
    return sorted(file_array)

def dump_filedata(filename, sep='\t'):
    with open(filename, 'r') as fin:
        filedata = fin.read()
    return filedata

def sub_filedata(pattern, update, filedata, count=0):
    f = lambda x: re.sub(pattern, update, x, count=count)
    return np.array(list(map(f, filedata)))

def to_nd(r):
    return np.array([i for i in r])

def transpose_element(r, row, column=0):
    if row > 0:
        r[row - 1].insert(column, r[row][column])
    r[row][column] = r[row + 1][column ]
    del r[row + 1][column]
    return to_nd(r)

def clean_header(r):
    r = fix_header(r)
    while True:
        for t in (r'[oO0]{3,}', r'^[oO0]+$', r'^[\no O0]+$', r'\n[\n0oO]*$'):
            r[0] = sub_filedata(t, r'', r[0])
        if not np.all([i == '' for i in r[0]]):
            break
        r = np.delete(r, 0, axis=0)
    r[0] = sub_filedata(r' / ', r'/', r[0])
    return to_nd(r)

def clean_rows(r):
    u = list(r)
    s = [len(i) for i in r]
    p = np.argmax(np.bincount(s))
    for i in np.argwhere((s != p)).reshape(-1):
        v = [j for j in sub_filedata(r'[a-zA-Z]', r'', u[i]) if j != '']
        if len(v) == 0:
            del u[i]
        if len(v) == 1:
            j = u[i].index(v[0])
            u[i - 1][j] = u[i - 1][j] + v[0]
            del u[i]
        if len(v) > 1:
            if '-' in v:
                j = v.index('-')
                v[j+1] = v[j] + v[j+1]
                del v[j]
            u[i] = v
    return to_nd(u)

def get_emptyrow(filedata):
    return np.argwhere([j.all() for j in [i == '' for i in filedata]])

def del_emptyrow(filedata):
    return np.delete(filedata, get_emptyrow(filedata), axis=0)

def clean_list(r):
    if len(r[2]) == 1:
        r = transpose_element(r, 1)
    r = clean_header(r)
    if (r[0] == '').all() and len(r[1]) > len(r[0]):
        r = np.delete(r, 0, axis=0)
        r = np.array([i for i in r])
    if len(r.shape) == 1:
        r = clean_rows(r)
    if len(r.shape) == 1:
        122/0
    return r

def split_list(r):
    if np.array([('\t' in j) for i in r for j in i]).any():
         r = np.array([[k for j in i for k in j.split('\t')] for i in r])
    return r

def pd_report(r):
    r[0] = [re.sub(r'\s', r' ', i) for i in r[0]]
    r = pd.DataFrame(r).replace('', np.nan).dropna(how='all', axis=1).fillna('')
    r.columns = r.head(1).values.tolist()
    return r.drop(r.head(1).index).reset_index(drop=True)

def fix_header(r):
    for k in ['Appendix', 'fitted']:
        for i in r:
            if not np.any([k in j for j in i]):
                break
            r = np.delete(r, 0, axis=0)
    return to_nd(r)

def fix_header2(r):
    for u in r:
        for j in np.argwhere(u == 'C').reshape(-1):
            r[0][j] = r[0][j] + r[1][j]
            r[1][j] = ''
        if np.any([j in ['Ch', 'M'] for j in u]):
            break
        r = np.delete(r, 0, axis=0)
    if len(r[1]) == 1:
        transpose_element(r, 0)
        r = np.delete(r, 1, axis=0)
    return to_nd(r)

def get_report(filename, sep='\t'):
    r = get_reportdata(filename, sep=sep)
    r = clean_header(r)
    if sep == ' ':
        r = split_list(r)
        r = fix_header2(r)
    if len(r.shape) == 1:
        r = clean_list(r)
        r = clean_header(r)
    empty_row = get_emptyrow(r)
    r = del_emptyrow(r)
    if r.shape[0] == 0:
        return r
    r = clean_data(r)
    r = del_emptyrow(r)
    r = pd_report(r)
    return r

def get_reportdata(filename, sep='\t'):
    with open(filename, 'r', encoding='utf-8') as fin:
        filedata = fin.read()
    if not sep in filedata:
        sep = '\t'
    r = np.array(np.array([i for i in csv.reader(StringIO(filedata), delimiter=sep)]))
    return r

def clean_data(r):
    (m, n) = r.shape
    r = r.reshape(-1)
    for t in ((r'^\s+$', r''), (r'\n$', r''), (r'^\n', r''), (r'^[oO0]?([CM])', r'\1')):
        r = sub_filedata(*t, r)
    while True:
        i = np.argwhere(r[::n] == '')
        if not i.any():
            break
        if i[-1][0] < (m - 3):
            break
        if 'Gauge' in r and m < 5:
            break
        r = np.delete(r, n * i)
        n = n - 1
        if n < 1:
            3/0
        r = r[:n * m]
    r = r.reshape(m, n)
    return r

#args.all = False
#p = [365, 359, 391, 390, 817, 462, 451, 372, 402, 428, 430, 473, 496, 1061, 1098, 1136, 836, 544, 1037, 1145, 370, 886, 974, 901, 961, 785, 1156, 1060]

routes = [route]
if args.all:
    with open('section-list.json', 'r') as fin:
        routes = json.load(fin)
    routes = dict((k, d[k]) for d in routes for k in d)

def add_row(df, nrow=0):
    df.index = df.index + 1
    df.loc[nrow] = [''] * len(df.columns)
    df = df.sort_index()
    return df

REPORT = {}
for route in routes:
    reportfiles = get_files(None, '{}'.format(route), '_1.tsv', ignorecase=True)
    #reportfiles = get_files(None, '{}'.format(route), '{}_1.tsv'.format(p[-1]), ignorecase=True)
    for reportfile in reportfiles:
        filepath = path.dirname(reportfile)
        filestub = path.basename(reportfile[:-6])
        page = filestub[3:]
        try:
            report_1 = get_report('{}/{}_1.tsv'.format(filepath, filestub))
            report_2 = get_report('{}/{}_2.tsv'.format(filepath, filestub), sep=' ')
            report_3 = get_report('{}/{}_3.tsv'.format(filepath, filestub))
            if report_1.shape[0] != report_2.shape[0]:
                print('ERROR rows 1:2 mismatch: Route {} page {}'.format(route, page))
                continue
            if report_1.shape[0] != report_3.shape[0]:
                if 'Gauge' not in report_3:
                    print('ERROR row 1:3 mismatch: Route {} page {}'.format(route, page))
                    continue
                report_1 = add_row(report_1)
                report_2 = add_row(report_2)
                if report_1.shape[0] != report_3.shape[0]:
                    print('ERROR row 1:3 mismatch: Route {} page {}'.format(route, page))
                    continue
            df1 = pd.concat([report_1, report_2, report_3], axis=1)
        except FileNotFoundError:
            df1 = report_1
            if not df1.index.any() or not 'Gauge' in df1.columns:
                continue
            if df1.iloc[0, 1] != '':
                v = df1.iloc[0].tolist()
                v.insert(0, '')
                v = v[:-1]
                df1.iloc[0, :] = v
                a = [df1.columns.levels[0][i] for i in df1.columns.labels[0]]
                a[3], a[-1] = a[-1], a[3]
                df1.columns = pd.MultiIndex.from_arrays([a])
        except IndexError:
            continue
        c = [i[0] for i in df1.columns.values]
        (n, m) = report_1.shape

        if not args.all:
            print(route, page)

        if 'ELR' in df1.columns or 'Gauge' in df1.columns:
            #if not args.all:
            #    print(route, page)
            key = '\t'.join([re.sub(r'\s', r' ', i[0]) for i in df1.columns.tolist()])
            hkey = hashlib.md5(key.encode()).hexdigest()
            df1['Route'] = route
            df1['page'] = page
            df1['seq'] = df1.index + 1
            df2 = df1.iloc[:, -3:]
            df2 = df2.join(df1.iloc[:, :-3])
            df2.to_csv('report/{}_{}.tsv'.format(route, page), index=False, sep='\t')
