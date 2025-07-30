import os

def save_first_network(file_path, weighted):
    g1 =os.path.join(file_path, "ntwk", "1.txt")
    output_path = os.path.join(file_path, "changed")
    os.makedirs(output_path, exist_ok=True)
    output_txt_path = os.path.join(output_path ,"1.txt")
    with open(g1, 'r') as file:
        g_l1 = file.readlines()
        with open(output_txt_path, 'w') as output_file:
            output_file.write("# New Edges:\n")
            for line in g_l1:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    if  not weighted:
                        a, b = int(parts[0]), int(parts[1])
                        edge = (a, b) if a < b else (b, a)
                        output_file.write(f"{str(edge[0])}\t{str(edge[1])}\n")
                    else:
                        a, b, w = int(parts[0]), int(parts[1]), parts[2]
                        edge = (a, b) if a < b else (b, a)
                        output_file.write(f"{edge[0]}\t{edge[1]}\t{w}\n")

def filter_changed_nodes(file_path, weighted):
    i = 1
    e_save = None
    print("Processing:", end=" ")
    while True:
        print(i, end=" ")
        g1 = os.path.join(file_path, "ntwk", f"{i}.txt")
        g2 = os.path.join(file_path, "ntwk", f"{i+1}.txt")

        if not (os.path.exists(g1) and os.path.exists(g2)): break
        if  e_save:
            e1 = e_save
        else:
            e1 = set()
            with open(g1, 'r') as file:
                g_l1 =  file.readlines()
            for line in g_l1:
                if line.strip():
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        if not weighted:
                            a, b = int(parts[0]), int(parts[1])
                            edge = (a, b) if a < b else (b, a)
                            e1.add(edge)
                        else:
                            a, b, w = int(parts[0]), int(parts[1]), float(parts[2])
                            edge = (a, b, w) if a < b else (b, a, w)
                            e1.add(edge)

        e2 = set()
        with open(g2, 'r') as file:
            g_l2 =  file.readlines()
            for line in g_l2:
                if line.strip():
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        if not weighted:
                            a, b = int(parts[0]), int(parts[1])
                            edge = (a, b) if a < b else (b, a)
                            e2.add(edge)
                        else:
                            a, b, w = int(parts[0]), int(parts[1]),float(parts[2])
                            edge = (a, b, w) if a < b else (b, a, w)
                            e2.add(edge)

        new_edges = e2 - e1
        del_edges = e1 - e2
        e_save = e2

        output_path = os.path.join(file_path, "changed")
        os.makedirs(output_path, exist_ok=True)
        output_txt_path =  os.path.join(output_path, f"{i+1}.txt")
        with open(output_txt_path, 'w') as output_file:
            output_file.write("# New Edges:\n")
            for edge in new_edges:
                if not weighted:
                    output_file.write(f"{str(edge[0])}\t{str(edge[1])}\n")
                else:
                    output_file.write(f"{str(edge[0])}\t{str(edge[1])}\t{str(edge[2])}\n")
            output_file.write("# Deleted Edges:\n")
            for edge in del_edges:
                if not weighted:
                    output_file.write(f"{str(edge[0])}\t{str(edge[1])}\n")
                else:
                    output_file.write(f"{str(edge[0])}\t{str(edge[1])}\t{str(edge[2])}\n")
        i += 1
    print("Done.")


def get_ntwk_change(path, weighted = False):
    
    save_first_network(path, weighted)
    filter_changed_nodes(path, weighted)