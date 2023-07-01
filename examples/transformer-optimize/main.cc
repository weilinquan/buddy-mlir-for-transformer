#include <cmath>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
typedef long int intptr_t;
// Define Memref Descriptor.
template <class ElementType>
struct Tensor_descriptor_ {
    ElementType *allocated;
    ElementType *aligned;
    intptr_t offset;
    intptr_t sizes[1];
    intptr_t strides[1];
};

extern "C" Tensor_descriptor_<float>* forward(Tensor_descriptor_<long long>*);
int main(){
    Tensor_descriptor_<long long>* arg0=(Tensor_descriptor_<long long>*)malloc(sizeof(Tensor_descriptor_<long long>));
    Tensor_descriptor_<float> *output;

    long long a[2][128];
    for(int i=0;i<2;i++){
        for(int j=0;j<128;j++){
            a[i][j]=1;
        }
    }
    arg0->aligned = (long long*)a;

    output = forward(arg0);

    printf("[");
    for(int i=0; i<30522; i++)
    {
    printf("%f\n ",*(output->aligned+i));
    }
    printf("]\n");
}