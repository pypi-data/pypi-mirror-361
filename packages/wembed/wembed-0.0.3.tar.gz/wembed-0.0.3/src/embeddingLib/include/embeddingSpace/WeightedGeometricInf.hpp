#pragma once

#include "Embedding.hpp"
#include "VecList.hpp"

class WeightedGeometricInf : public Embedding {
   public:
    WeightedGeometricInf(const std::vector<std::vector<double>> &coords, const std::vector<double> &weights);
    virtual ~WeightedGeometricInf(){};

    virtual double getSimilarity(NodeId a, NodeId b) const;
    virtual int getDimension() const;
    double getDistance(NodeId a, NodeId b) const;
    double getNodeWeight(NodeId a) const;

   private:
    const int DIMENSION;
    const double DINVERSE;
    VecList coordinates;
    std::vector<double> weights;
};
