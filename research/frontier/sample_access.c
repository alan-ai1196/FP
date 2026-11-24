#include <math.h>
#include <stdint.h>
#ifdef _WIN32
#define API __declspec(dllexport)
#else
#define API __attribute__((visibility("default")))
#endif

/* The evaluator reads the two base masses to score the issued probabilities.
   The model update in sampled mode reads only the two sample counts. */
API void access_stream(uint32_t n, const double *q, const uint8_t *y,
                       const uint8_t *draws, uint32_t budget, uint32_t packed,
                       const double *gain, void *carry, double *loss,
                       double *proposals) {
  double s[2];
  for (uint32_t i=0;i<2;++i)
    s[i]=packed?((int16_t*)carry)[i]/32767.0:((double*)carry)[i];
  for (uint32_t t=0;t<n;++t,q+=2,draws+=2) {
    double a=gain[0]*s[0],b=gain[1]*s[1];
    double wa=exp(a),wb=exp(b),z=(1.0-q[0]-q[1])+q[0]*wa+q[1]*wb;
    loss[t]=log(z)-(y[t]==0?a:(y[t]==1?b:0.0));
    proposals[t]=fmax(1.0,fmax(wa,wb))/z;
    for (uint32_t i=0;i<2;++i) {
      double observed=budget?((double)draws[i]/budget):q[i];
      s[i]+=((y[t]==i?1.0:0.0)-observed-s[i])/512.0;
      if (packed) {
        double code=round(s[i]*32767.0);
        code=fmax(-32767.0,fmin(32767.0,code));
        s[i]=code/32767.0;
      }
    }
  }
  for (uint32_t i=0;i<2;++i) {
    if (packed) ((int16_t*)carry)[i]=(int16_t)round(s[i]*32767.0);
    else ((double*)carry)[i]=s[i];
  }
}
