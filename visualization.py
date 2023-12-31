from pyvis.network import Network as Network
from scipy.sparse import coo_matrix
import json
import os
import numpy as np

relations_file = "./optimized_relations.json"
classification_file = "./classification_predictions.json"

type_dict = {0: "Claim", 1:"Claim", 2:"Premise"}
color_dict = {0: "#E11299", 1:"#E11299", 2:"#FDE2FE"}

def main():
    old_index = 0
    c_index = 0

    # get all files names in "classification" folder
    folder_path = "./classification"
    file_names = [f for f in os.listdir(folder_path) if f.endswith('.json')]

    # Remove the '.json' extension
    file_names = [file_name[:-5] for file_name in file_names]  

    # Sort the files
    file_names = sorted(file_names)

    # test_counter used to break limit the number of files for testing
    test_counter=0

    # For each file
    persuasive_dict = {}
    for essay in file_names:
        if test_counter >= 20:
            break;
        else:
            test_counter += 1
        nodes = [] # component indices for this essay
        labels = [] # claim or premise for this essay
        colors = [] # colors of each node for this essay
        edges = [] # [(1, 7)]
        hover_text = [] # component_text for this essay
        nodes_with_outgoing = []
        def get_components(essay):
            # Essay file: {0: ..., index, component_text, ...; 1, ...}
            with open(essay) as e_file:
                components = json.load(e_file)
            with open(classification_file) as c_file:
                classifications = json.load(c_file)
            for i in range(len(components)):
                nodes.append(components[i]["index"])
                hover_text.append(components[i]["component_text"])
                labels.append(str(components[i]["index"]) + type_dict.get(classifications[i + c_index]))
                colors.append(color_dict.get(classifications[i + c_index]))

        def get_relations(essay):
            with open(relations_file) as r_file:
                data = json.load(r_file)
            for str in data[essay]["relations"].keys():
                s, d = map(int, str.split(","))
                edges.append((s, d))
                nodes_with_outgoing.append(s)
        get_relations(essay)
        essay_file = f"./classification/{essay}.json"
        get_components(essay_file)
        old_index = c_index
        c_index += len(nodes)

        # get all the claims
        claims = set(nodes)
        # print(claims)
        # print(nodes_with_outgoing)
        claims -= set(nodes_with_outgoing)
        # print(claims)
        for x in nodes:
            if x in claims:
                colors[x-1] = "#E11299"
                labels[x-1] = str(x) + " Claim"
            else:
                colors[x-1] = "#FDE2FE"
                labels[x-1] = str(x) + " Premise"
        

        print(edges)
        if len(edges) > 0:
            rows, cols = zip(*edges)
            data = [1] * len(rows)
            # print(rows, cols)
            # print(data)

            # Creating a COO matrix
            n = c_index - old_index # matrix dimension n x n
            sparse_matrix = coo_matrix((data, (rows, cols)), shape=(n + 1, n + 1))

            # print(sparse_matrix)
            # row_sums = sparse_matrix.sum(axis=1)
            # row_sums = np.array(row_sums).squeeze().nonzero()[0]
            # print(row_sums)

            column_sums = sparse_matrix.sum(axis=0)
            print(claims)
            claims_wo = len(claims - set(np.array(column_sums).squeeze().nonzero()[0]))
            claims_w = len(claims) - claims_wo
            # print()
            print(f"Claims with supporting premises: {claims_w}")
            print(f"Claims without supporting premises: {claims_wo} ")
            
            # what if claims_w is 0?
            if len(claims) != 0:
                persuasiveness = claims_w / len(claims)
                print(f"Persuasiveness: {claims_w / len(claims)}")
            else:
                persuasiveness = 1
                print(f"Persuasiveness: {1}")
            
            persuasive_dict[essay] = str(round(persuasiveness * 100, 1)) + "%"
        else:
            persuasive_dict[essay] = str(0) + "%"
        # print()
        # print("Sparse Matrix:")
        # print(sparse_matrix.tocsr())

        net = Network(directed=True)
        net.add_nodes(nodes, label=labels, color=colors, title=hover_text)
        net.add_edges(edges)
        net.show(f"./visualizations/visualize{essay}.html", notebook=False)

        print(f"Done with {essay}: {c_index - old_index} Components")
    
    # Serializing json
    json_object = json.dumps(persuasive_dict, indent=4)
 
    # Writing to sample.json
    with open("persuasiveness.json", "w") as outfile:
        outfile.write(json_object)


if __name__ == "__main__":
    main()