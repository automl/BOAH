import os

from cave.cavefacade import CAVE

def analyze_all():
    for dirpath, dirnames, filenames in os.walk('../opt_results/'):
        if not dirnames:
            print(dirpath)
            cave = CAVE(folders=[dirpath],
                        output_dir=os.path.join("../CAVE_reports", dirpath[15:]),  # output for debug/images/etc
                        ta_exec_dir=["."],                            # Only important for SMAC-results
                        file_format='BOHB' if os.path.exists(os.path.join(dirpath, 'configs.json')) else 'SMAC3',
                        #verbose_level='DEV_DEBUG',
                        verbose_level='OFF',
                        show_jupyter=False,
                        )
            cave.analyze()

if __name__ == '__main__':
    analyze_all()
