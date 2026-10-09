import path_utilities as rp
import generate_graf as gp
import Metrics as mr
import random
import pandas as pd
import GeneticAlgorithm as ga

def population(G,source,target,size):
    # population creation
    pop_list=[]
    tester=0
    while tester<(size*10):# Gave 10 trials per requested individual (10x the requested size). Each path gets 10 chances to enter.
        list1=rp.generate_random_path(G,source,target)# Got random paths with the random path generator function
        if list1!=None and list1 not in pop_list and len(list1)>=2:# Check if this path exists, whether it is already in the population, and whether it has at least 2 nodes
            pop_list.append(list1)

        if len(pop_list)==size:# If population fills early, break the loop.
            break
        tester+=1
    return pop_list


def fitness_calculation(G,pop_list,w_delay=0.5, w_rel=0.1,w_band=0.4,max_delay=100,demand_mbps=0.2):
    # fitness calculation function, actually cost is calculated here. Lower value is better.
    pop_fit=[]
    #w_delay+w_rel+w_band=1. This equation is required.

    for pop in pop_list:# Here the cost of each population member is calculated one by one, using my metrics class.
        TotalDelay=mr.Total_Delay(G,pop)
        TotalReliability=mr.Total_Reliability(G,pop)
        TotalBandwidth=mr.Total_Bandwidth(G,pop)
        min_mbps=float('inf')

        for temp in range(len(pop)-1):
            u=pop[temp]
            v=pop[temp+1]
            mbps=G.edges[u,v]['bandwidth_mbps']
            if mbps<min_mbps:
                min_mbps=mbps


        if TotalDelay > max_delay:# If total delay is higher than our max_delay, trash its value. Goal is to prevent that path from being selected.
            fitness = 999999
        elif demand_mbps>min_mbps:
            fitness = 999999
        else:
            fitness=((TotalDelay*w_delay)+(TotalReliability*w_rel)+(TotalBandwidth*w_band))

        pop_fit.append((pop,fitness))# Here both the path and its cost are added as a tuple.

    return pop_fit

def get_parent(pop_fit):# Goal here is to increase diversity. Returns only one path. I.e. selects one individual.
    select_temp=[]

    if len(pop_fit)==0:
        return None

    if len(pop_fit)<=4:
        select_temp=pop_fit.copy()# If 4 or fewer, copy directly.
    else:
        count = 0
        while len(select_temp) < 4 and count < 50:  # Try to pick 4 random distinct ones. Counter added so it does not struggle too long.
            temp = random.choice(pop_fit)
            if temp not in select_temp:
                select_temp.append(temp)
            count += 1

        while len(select_temp) < 4:  # If still not selected, keep adding until selected.
            tempeture = random.choice(pop_fit)
            select_temp.append(tempeture)
    candidates=[]
    weights=[]

    for path,fitness in select_temp:# Calculated weights of those paths for roulette-wheel selection.
        candidates.append(path)
        weight=1/(fitness+0.0001)# Added 0.0001 to avoid 0 in denominator.
        weights.append(weight)

    selected=random.choices(candidates,weights=weights,k=1)# Done so that those with almost equal fitness values have equal selection chances.

    return selected[0]# Returned the selected path.

def selection(pop_fit):
    father=get_parent(pop_fit)
    mother=get_parent(pop_fit)

    return father,mother



def crossover(father,mother):
    if father==None or mother==None:# If mother or father is missing, there is no child.
        return None

    common_node=[node for node in father if node in mother]# Took common points for crossover.
    child=[]

    if len(common_node)<2:# If fewer than 2 common points, there is no common point. Source and target must already be guaranteed.
        return None

    for index in range(len(common_node)-1):
        u=common_node[index]# Since common points were taken in order, take the first and the next common point here.
        v=common_node[index+1]

        indFaU=father.index(u)# Take the father's common point index here.
        indFaV=father.index(v)
        listFa=father[indFaU:indFaV]# Cut using the taken indices.

        indMoU=mother.index(u)# Same scenario applies to the mother.
        indMoV=mother.index(v)
        listMo=mother[indMoU:indMoV]

        rand_cho=random.choice([listFa,listMo])# Randomly choose between them.
        child.extend(rand_cho) # Add one by one to the list.

    child.append(common_node[-1])# Finally add the target.
    return rp.yolu_Sadelestir(child)# Simplify the path with the simplify-path function and return that value.

def multi_mutation(G,child,mutation_rate=0.1):

    if random.random() < mutation_rate and len(child)>2:# Roll the dice. If it hits, mutate. Also child length must be > 2. (S,T)
        temp=None
        roll=random.random()
        if roll<0.60:
            temp=mutation_version1(G,child)
        elif roll<0.80:
            temp=mutation_version2(G,child)
        else:
            temp=mutation_version3(G,child)

        if temp==None:# If empty, no mutation applied. If a full path arrived, simplify it with the simplify-path function and return the value.
            return child
        else:
            return rp.yolu_Sadelestir(temp)
    else:
        return child

def mutation_version1(G,child):# E.g. path:1-2-3-4-5-6-7-8-9 -> mutated path:1-2-3-4-15-6-8-9
    choice = random.randint(1, len(child) - 2)  # Got a random index. Excluded source and target.
    temp = child[:choice + 1]  # Took everything up to and including the selected point.
    temp = rp.tamamla_path(G, temp, child[-1])  # Completed the path with the complete-path function.
    return temp

def mutation_version2(G,child):# E.g. path:1-2-3-4-5-6-7-8-9 mutated path:1-24-54-32-34-5-6-7-8-9
    choice = random.randint(1, len(child) - 2)
    child_head=child[:choice + 1]
    tail=child[choice:]
    temp_target=child[choice]
    temp_source=child[0]
    counter=0
    head=None
    while counter<10:
        head=rp.generate_random_path(G,temp_source,temp_target)
        if head is not None and head!=child_head:
            break
        counter+=1
    if head is None:return None
    temp=head[:-1]+tail
    return temp

def mutation_version3(G,child):# E.g. path:1-2-3-4-5-6-7-8-9 mutated path: 1-2-3-4-54-65-76-32-43-8-9
    if len(child)>4:
        count=0
        while count<10:
            choice1 = random.randint(1, len(child) - 2)
            choice2 = random.randint(1, len(child) - 2)
            if abs(choice1 - choice2) > 1:
                break
            else:
                count+=1
        if count==10:return child
        firstIndex=min(choice1, choice2)
        lastIndex=max(choice1, choice2)
        temp_head=child[:firstIndex+1]
        tail=child[lastIndex:]
        header=rp.tamamla_path(G,temp_head,child[lastIndex])
        if header is not None:
            mutation_child=header+tail[1:]
            return mutation_child
        else:return None
    else:
        return None

def genetic_algorithm(G,source,target,demand_mbps,pop_size=50,generations=3000,mutation_rate=0.1,w_delay=0.33,w_rel=0.33,w_band=0.34,max_delay=100):
    #Main part
    population_group=population(G,source,target,pop_size)# Created the population.
    global_best_value=99999# Gave best value 999999 for now. Later if best value never changes, temporarily increase mutation rate.
    mutation_value_count=0# Counter for the line above.
    current_mutation_rate=mutation_rate# Made a temporary mutation rate so the original rate is not lost. We will work with this one to reuse the old rate.

    for i in range(generations):# Created for how many generations to run.
        fitness_group = fitness_calculation(G, population_group, w_delay, w_rel, w_band,max_delay,demand_mbps)# Fitness values calculated.
        best_generetion=[]# Created for children.
        fitness_group.sort(key=lambda x: x[1])# Sorted first. Because in the starred place below, the best two individuals are added to the group so they are not lost.

        if fitness_group[0][1] < global_best_value:# Done to increase mutation rate. If best value found, reset the counter.
            global_best_value=fitness_group[0][1]
            mutation_value_count=0
            current_mutation_rate=mutation_rate
        else:# If best value still not returned, increase the counter.
            mutation_value_count+=1

        if mutation_value_count==10:# If still no best value for 10 generations, increase the mutation rate.
            current_mutation_rate=0.3

        if mutation_value_count==20:# At 20 generations, restore the mutation rate.
            current_mutation_rate = mutation_rate

        if rp.yol_gecerli_mi(G,fitness_group[0][0],source,target):#***** Also checked if path is valid. Copied it in case value gets corrupted. Did not take reference.
            best_generetion.append(fitness_group[0][0][:])# Copied, did not take reference.

        if rp.yol_gecerli_mi(G,fitness_group[1][0],source,target):#***** Also checked if path is valid. Copied it in case value gets corrupted. Did not take reference.
            best_generetion.append(fitness_group[1][0][:])# Copied, did not take reference.

        child_count=0# Counter created for how many times a child failed to be added in the while loop.
        generation_count=0# Counter added so it does not struggle too much if best_generation never fills. 1000 tries per generation.

        while len(best_generetion)<pop_size and generation_count<1000:

            father, mother = selection(fitness_group)# Parents are selected.
            child = crossover(father, mother)# Crossover is done.

            if child is None: continue# If no child, continue.

            child = multi_mutation(G, child, current_mutation_rate)# Mutation applied, if applicable.

            if rp.yol_gecerli_mi(G,child, source,target):# Check via the is-path-valid function whether the path exists. Returns True or False.
                if child not in best_generetion or child_count>15:# If child is not in best_generation or counter exceeded 15, add the child.
                    best_generetion.append(child)
                    child_count=0
                else:
                    child_count+=1
            generation_count+=1

        population_group=best_generetion# Finally the created children will make children to form the next generation. I.e. they will be parent selections.


    fitness_group = fitness_calculation(G, population_group, w_delay, w_rel, w_band,max_delay,demand_mbps)# Finally calculated fitness (cost) of the best paths formed.
    fitness_group.sort(key=lambda x:x[1])# Sorted. Lowest cost first.
    return fitness_group[0][0]# Returned the best.




def read_demands(filename):# File reading operations
    try:
        df = pd.read_csv(filename, sep=";")
        rows = []
        for index, row in df.iterrows():
            source = int(row["src"])
            target = int(row["dst"])
            str_band = str(row["demand_mbps"])

            band = float(str_band.replace(",", "."))
            one_row = (source, target, band)
            rows.append(one_row)

        return rows
    except Exception as e:
        print(f"File read error : {e}")
        return []


def main():
    print("==========================================")
    print("      GENETIC ALGORITHM NETWORK SIMULATION     ")
    print("==========================================\n")

    # 1. File names
    demand_file = "data/BSM307_317_Guz2025_TermProject_DemandData(in)(1).csv"

    # 2. Load the graph
    print("📡 Step 1: Loading network topology (graph)...")
    try:
        G = gp.graf_uret()  # Graph generator function
        print(f"   ✅ Graph created successfully ({len(G.nodes)} nodes, {len(G.edges)} edges)\n")
    except Exception as e:
        print(f"   ❌ Error while creating graph: {e}")
        return

    # 3. Read demands
    print(f"📋 Step 2: Reading demand file ({demand_file})...")
    demands = read_demands(demand_file)
    print(f"   ✅ Total {len(demands)} demands to process.\n")

    # 4. Run the algorithm for each demand
    print("🚀 Step 3: Simulation starting...\n")

    successful_routes = 0

    # Weight settings (MUST be the same as defaults in the GA function)
    # If you don't pass weights externally to the GA function, write the defaults here:
    w_delay = 0.33
    w_rel = 0.33
    w_band = 0.34

    for i, (src, dst, bw_demand) in enumerate(demands):
        print(f"🔹 Demand {i + 1}: Source {src} -> Destination {dst} | Requested speed: {bw_demand} Mbps")

        # Call the algorithm
        try:
            best_path = ga.genetic_algorithm(
                G,
                source=src,
                target=dst,
                demand_mbps=bw_demand,
                pop_size=50,
                generations=3000,
                mutation_rate=0.1,
                max_delay=200,
                # Write weights here too, to be safe:
                w_delay=w_delay, w_rel=w_rel, w_band=w_band
            )

            # Result check
            if best_path:
                print(f"   ✅ PATH FOUND: {best_path}")

                # --- FITNESS CALCULATION ADD-ON ---
                d_val = mr.Total_Delay(G, best_path)
                r_val = mr.Total_Reliability(G, best_path)
                b_val = mr.Total_Bandwidth(G, best_path)

                # Fitness formula: (Delay*w) + (Reliability*w) + (Bandwidth*w)
                fitness_score = (d_val * w_delay) + (r_val * w_rel) + (b_val * w_band)

                print(f"   📊 Delay: {d_val:.2f} ms")
                print(f"   🧬 Fitness Score: {fitness_score:.4f}")
                # -----------------------------------

                successful_routes += 1
            else:
                print("   ❌ NO SUITABLE PATH FOUND (insufficient capacity or disconnection)")

        except Exception as e:
            print(f"   ⚠️ Algorithm error: {e}")

        print("-" * 40)

    print(f"\n🏁 Simulation completed.")
    print(f"📊 Success rate: {successful_routes}/{len(demands)}")


if __name__ == "__main__":

    main()
