from AgentBasedModeling.helpers.game_of_life.game import GameOfLife
import os


root = os.path.dirname(os.path.abspath(__file__))

for s_dir_path, _, files in os.walk(os.path.join(root, 'Games')):
    files = [file for file in files if file == 'state.csv']
    if files:
        file_path = os.path.join(s_dir_path, files[0])
        if os.path.basename(s_dir_path) == 'Glider':
            gol = GameOfLife.from_csv(file_path, borders=[1, 2, 3, 4])
        elif os.path.basename(s_dir_path) in {'HWSS', 'LWSS'}:
            gol = GameOfLife.from_csv(file_path, borders=['right', 'left'])
        else:
            gol = GameOfLife.from_csv(file_path)
        gol.link_cells()
        gol.process()
        gol.plotting_engine.animate()
