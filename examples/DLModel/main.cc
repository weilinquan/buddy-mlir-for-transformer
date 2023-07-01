#include <stdlib.h>
#include <stdio.h>
typedef long int intptr_t;
// Define Memref Descriptor.
typedef struct Tensor_descriptor_* Tensor_descriptor;
typedef struct Tensor_descriptor_ {
float *aligned;
} Tensor;
Tensor forward(Tensor *);
int main()
{
Tensor *arg0= (Tensor *)malloc(sizeof(Tensor));
Tensor output;
float a[1][3][224][224];
for(int i=0;i<1;i++){
    for(int j=0;j<3;j++){
        for(int m=0;m<224;m++){
            for(int n=0;n<224;n++){
                a[i][j][m][n]=1;
            }
        }
    }
}
arg0->aligned = (float*)a;

output = forward(arg0);

printf("[");
for(int i=0; i<1000; i++)
{
printf("%f ",*(output.aligned+i));
}
printf("]\n");
}