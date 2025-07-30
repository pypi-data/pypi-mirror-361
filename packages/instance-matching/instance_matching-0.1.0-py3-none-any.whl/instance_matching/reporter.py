import os
import sys
import numpy as np
import pickle as pkl


class Reporter:
    def __init__(self, mode):
        """
        mode: 'matching', 'update', or 'update-base'
        """
        self.mode           = mode
        self.report         = {}   # map_name → report data
        self.initialized    = {}
        self.methods_order  = {}
        self.prev_lines     = {}   # map_name → how many lines we printed last time

    def update(self, name, input_reports):
        if not input_reports:
            return

        if self.mode == 'matching':
            instance_types = ['center_lines', 'lane_dividers']
            if name not in self.report:
                self.report[name]       = {}
                self.initialized[name]  = False
                self.methods_order[name]= []
                sample = input_reports[0]
                for m in sample:
                    # zero‐initialize all counts
                    self.report[name][m] = {
                        inst: {'TP':0,'FP':0,'FN':0,'Total':0,'n12':0,'d12':0,'n21':0,'d21':0}
                        for inst in instance_types
                    }
                    self.report[name][m]['cross_TCS'] = {'n12':0,'d12':0,'n21':0,'d21':0}
                    self.methods_order[name].append(m)

            # accumulate
            for rep in input_reports:
                for m in rep:
                    for inst in ['center_lines','lane_dividers']:
                        for key in ('TP','FP','FN','Total','n12','d12','n21','d21'):
                            self.report[name][m][inst][key] += rep[m][inst][key]
                    for key in ('n12','d12','n21','d21'):
                        self.report[name][m]['cross_TCS'][key] += rep[m]['cross_TCS'][key]

        elif self.mode in ('update','update-base'):
            # store the latest evaluate() report
            self.report[name] = input_reports[-1]
            # ensure we have a prev_lines slot
            if name not in self.prev_lines:
                self.prev_lines[name] = 0

    def print(self, map_name, trip_iter, tripN, frame_iter, frameN, verbose=0):
        if verbose != 0:
            return

        if self.mode == 'matching':
            # — your original print logic unchanged
            methods = self.methods_order[map_name]
            num_methods = len(methods)
            tp = np.zeros(num_methods)
            fp = np.zeros(num_methods)
            fn = np.zeros(num_methods)
            n12, d12, n21, d21 = (np.zeros(num_methods) for _ in range(4))
            n12c, d12c, n21c, d21c = (np.zeros(num_methods) for _ in range(4))

            if not self.initialized.get(map_name, False):
                self.initialized[map_name] = True
                print(f"Map: {map_name:<20} | Trip: {trip_iter}/{tripN} | Frame: {frame_iter}/{frameN}")
                for _ in range(num_methods):
                    print("...")

            for i, m in enumerate(methods):
                for inst in ['center_lines','lane_dividers']:
                    tp[i]  += self.report[map_name][m][inst]['TP']
                    fp[i]  += self.report[map_name][m][inst]['FP']
                    fn[i]  += self.report[map_name][m][inst]['FN']
                    n12[i] += self.report[map_name][m][inst]['n12']
                    d12[i] += self.report[map_name][m][inst]['d12']
                    n21[i] += self.report[map_name][m][inst]['n21']
                    d21[i] += self.report[map_name][m][inst]['d21']
                n12c[i] += self.report[map_name][m]['cross_TCS']['n12']
                d12c[i] += self.report[map_name][m]['cross_TCS']['d12']
                n21c[i] += self.report[map_name][m]['cross_TCS']['n21']
                d21c[i] += self.report[map_name][m]['cross_TCS']['d21']

            # calculate scores
            prec = np.where(tp+fp>0, tp/(tp+fp), 0.0)
            rec  = np.where(tp+fn>0, tp/(tp+fn), 0.0)
            f1   = np.where(prec+rec>0, 2*prec*rec/(prec+rec), 0.0)
            tcs12 = np.where(d12>0, n12/d12, 0.0)
            tcs21 = np.where(d21>0, n21/d21, 0.0)
            tcs   = np.where(tcs12+tcs21>0, 2*tcs12*tcs21/(tcs12+tcs21), 0.0)
            ctcs12 = np.where(d12c>0, n12c/d12c, 0.0)
            ctcs21 = np.where(d21c>0, n21c/d21c, 0.0)
            ctcs   = np.where(ctcs12+ctcs21>0, 2*ctcs12*ctcs21/(ctcs12+ctcs21), 0.0)

            max_len   = max(len(m) for m in methods)
            total_ln  = num_methods + 1

            # clear and reprint
            for _ in range(total_ln):
                sys.stdout.write('\033[2K'); sys.stdout.write('\033[1A')
            sys.stdout.write('\033[2K')
            header = f"Map: {map_name:<20} | Trip: {trip_iter}/{tripN} | Frame: {frame_iter}/{frameN}"
            sys.stdout.write(header + '\n')
            for m, f1s, tcs_s, ctcs_s in zip(methods, f1, tcs, ctcs):
                line = f"{m:<{max_len}} | F1={f1s:.3f} | TCS={tcs_s:.3f} | CTCS={ctcs_s:.3f}"
                sys.stdout.write(line + '\n')
            sys.stdout.flush()

        elif self.mode in ('update','update-base'):
            # — handle evaluate()-style report
            report = self.report.get(map_name)
            if report is None:
                return

            # clear previous
            prev = self.prev_lines.get(map_name, 0)
            for _ in range(prev):
                sys.stdout.write('\033[2K'); sys.stdout.write('\033[1A')
            sys.stdout.write('\033[2K')

            # reprint header
            header = f"Map: {map_name:<20} | Trip: {trip_iter}/{tripN} | Frame: {frame_iter}/{frameN}"
            sys.stdout.write(header + '\n')
            lines = 1

            # print Average Precision
            sys.stdout.write("Average Precision:\n"); lines += 1
            for inst, val in report['AP'].items():
                sys.stdout.write(f"  {inst:<15}: {val:.3f}\n"); lines += 1
            sys.stdout.write(f"  {'mAP':<15}: {report['mAP']:.3f}\n"); lines += 1

            # intra-type edges
            sys.stdout.write("Intra-type F1:\n"); lines += 1
            for inst, m in report['edge'].items():
                sys.stdout.write(
                    f"  {inst:<15} | P={m['precision']:.3f} "
                    f"R={m['recall']:.3f} F1={m['f1_score']:.3f}\n"
                )
                lines += 1

            # cross-type edges
            sys.stdout.write("Cross-type F1:\n"); lines += 1
            for side, m in report['cross_edge'].items():
                sys.stdout.write(
                    f"  {side:<15} | P={m['precision']:.3f} "
                    f"R={m['recall']:.3f} F1={m['f1_score']:.3f}\n"
                )
                lines += 1

            sys.stdout.flush()
            self.prev_lines[map_name] = lines

    def save(self, map_name=None, save_path=None):
        """
        Save the report dictionary to a file.
        If map_name is given, save only that map's report.
        Filename is prefixed by the mode, e.g.:
        matching_report_{}.pkl
        update_report_{}.pkl
        update_base_report_{}.pkl
        """
        # sanitize mode to use as filename prefix
        prefix = self.mode.replace('-', '_')

        if map_name:
            data = self.report.get(map_name, {})
            safe_name = map_name.replace('-', '_')
            filename = save_path or f"{prefix}_report_{safe_name}.pkl"
        else:
            data = self.report
            filename = save_path or f"{prefix}_report.pkl"

        # ensure directory exists
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)

        # write out
        with open(filename, 'wb') as f:
            pkl.dump(data, f)

        print(f"Report saved to {filename}")
        