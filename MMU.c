#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define page_table_size 256
#define page_size 256
#define TLB_size 16
#define frame_size 256

struct page_table_entry{
    int frame;
    int valid;
    int update_time;
};

struct TLB_entry{
    int page;
    int frame;
};

struct page_table_entry page_table[page_table_size];
struct TLB_entry TLB[TLB_size];

// debug
char *state;

int search_page_table(int page_num);
int search_TLB(int page_num);
void update_page_table(int page_num, int frame_num, int time);
void update_TLB(int page_num, int frame_num);

// memory frame count
int memory_count = 0;
int TLB_count = 0;
void fill_in_memory();

int main(int argc, char *argv[]){
    // init TLB
    int l;
    for(l=0;l<TLB_size;l++){
        TLB[l].frame = -1;
        TLB[l].page = -1;
    }

    // init page table
    for(l=0;l<page_table_size;l++){
        page_table[l].frame = -1;
        page_table[l].valid = 0;
        page_table[l].update_time = -1;
    }

    int logical_address;
    int physical_address;
    int page_number;
    int frame_number;
    int offset;
    float total_address_count = 0;
    float page_fault_count = 0;
    float TLB_hit_count = 0;
    signed char values[256];
    signed char value;

    int clock = 0;

    // if(argc != 4){
    //     printf("wrong number of argument");
    //     exit(0);
    // }

    int memory_size = atoi(argv[1]);
    signed char *physical_memory[memory_size][frame_size];
    char *disk = argv[2];
    char *input = argv[3];
    char *result;

    if(memory_size == 128){
        result = "output128.csv";
    }
    else if(memory_size == 256){
        result = "output256.csv";
    }
    else{
        printf("wrong number of memory size");
        exit(0);
    }

    FILE *backing_store = fopen(disk,"r");
    FILE *address = fopen(input,"r");
    FILE *output = fopen(result, "w");

    signed char input_line[16];
    while(fgets(input_line, 16, address)){
        total_address_count++;
        clock++;

        logical_address = atoi(input_line);
        page_number = (logical_address >> 8) & 0xFF;
        offset = logical_address & 0xFF;

        int TLB_frame = search_TLB(page_number);
        if(TLB_frame >= 0){
            // found in TLB
            frame_number = TLB_frame;
            // update update_time
            page_table[page_number].update_time = clock;
            // TLB hit
            TLB_hit_count++;
            state = "TLB hit";
        }
        else{
            // not found in TLB
            // go to page table
            int page_table_frame = search_page_table(page_number);
            if(page_table_frame >= 0){
                // found in page table
                frame_number = page_table_frame;
                // update update_time
                page_table[page_number].update_time = clock;
                // update TLB
                update_TLB(page_number,frame_number);
                state = "IN PAGE";
            }
            else{
                // not found in page table
                // page fault
                page_fault_count++;
                state = "OUT PAGE";
                // go to backing store
                if(fseek(backing_store, 256*page_number, SEEK_SET) == 0){
                    fread(values, frame_size, 1, backing_store);
                    // if memory is full
                    if(memory_count == memory_size){
                        // find out which to page out using LRU
                        int b;
                        int min;
                        int page_out_index;
                        for(b=0;b<page_table_size;b++){
                            if(page_table[b].valid){
                                min = page_table[b].update_time;
                                page_out_index = b;
                                break;
                            }
                        }

                        for(b=0;b<page_table_size;b++){
                            if(page_table[b].valid){
                                if(page_table[b].update_time < min){
                                    min = page_table[b].update_time;
                                    page_out_index = b;
                                }
                            }
                        }

                        // get newly free frame number
                        frame_number = page_table[page_out_index].frame;

                        // remove old from page table
                        page_table[page_out_index].frame = -1;
                        page_table[page_out_index].valid = 0;
                        page_table[page_out_index].update_time = -1;

                        memory_count--;
                    }
                    else{
                        // memory is not full
                        frame_number = memory_count;
                    }

                    // fill in memory
                    int j;
                    for(j=0;j<frame_size;j++){
                        physical_memory[frame_number][j] = values[j];
                    }
                    
                    //update page table and TLB
                    update_page_table(page_number, frame_number, clock);
                    update_TLB(page_number, frame_number);
                    memory_count++;
                    // // data debug
                    // if(logical_address == 64390){
                    //     int test = (logical_address >> 8) & 0xFF;
                    //     printf("input 64390: %d, %d, %d\n", logical_address,page_table[page_number].frame, value);
                    // }
                }
                else{
                    // error
                    printf("backing store error");
                }
            }
        }
        physical_address = frame_number*frame_size+offset;
        value = physical_memory[frame_number][offset];
        fprintf(output, "%d,%d,%d\n", logical_address, physical_address, value);
        // debug
        // fprintf(output, "%s page: %d frame: %d off: %d\n", state, page_number, frame_number*frame_size, offset);
    }

    fprintf(output, "Page Faults Rate, %.2f%%,\n", page_fault_count*100/total_address_count);
    fprintf(output, "TLB Hits Rate, %.2f%%,", TLB_hit_count*100/total_address_count);

    // close file
    fclose(backing_store);
    fclose(address);
    fclose(output);
}

int search_page_table(int page_num){
    if((page_table[page_num].valid) == 1){
        return page_table[page_num].frame;
    }
    else{
        return -1;
    }
}

int search_TLB(int page_num){
    int i;
    int found = 0;
    for(i=0;i<TLB_size;i++){
        if(TLB[i].page == page_num){
            found = 1;
            return TLB[i].frame;
            break;
        }
    }
    // case of not found
    if(found == 0){
        return -1;
    }
}

void update_page_table(int page_num, int frame_num, int time){
    page_table[page_num].frame = frame_num;
    page_table[page_num].update_time = time;
    page_table[page_num].valid = 1;
}

void update_TLB(int page_num, int frame_num){
    if(TLB_count < TLB_size){
        TLB[TLB_count].frame = frame_num;
        TLB[TLB_count].page = page_num;
        TLB_count++;
    }
    else{
        int t;
        for(t=0;t<TLB_size-1;t++){
            TLB[t].frame = TLB[t+1].frame;
            TLB[t].page = TLB[t+1].page;
        }
        TLB[TLB_size-1].frame = frame_num;
        TLB[TLB_size-1].page = page_num;
    }
}