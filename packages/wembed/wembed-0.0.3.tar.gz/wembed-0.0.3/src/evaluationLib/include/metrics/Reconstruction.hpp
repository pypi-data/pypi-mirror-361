#pragma once

#include <memory>

#include "Embedding.hpp"
#include "Graph.hpp"
#include "Metric.hpp"
#include "NodeSampler.hpp"
#include "VecList.hpp"

/**
 * Calculate reconstruction.
 * For every node, calculate the average precision or precision at dregree. The mean of these values is reported.
 * Only a fraction of the nodes are sampled (and at most 5000), because the runtime for every node is in O(n)
 */
class Reconstruction : public Metric {
   public:
    Reconstruction(const Graph &g, std::shared_ptr<Embedding> embedding, int numNodeSamples)
        : graph(g), embedding(embedding), numNodeSamples(numNodeSamples), buffer(embedding->getDimension()) {};

    std::vector<std::string> getMetricValues();
    std::vector<std::string> getMetricNames();

   private:
    // currently unused
    static void writeHistogram(const std::vector<nodeEntry> &entries);

    const Graph &graph;
    std::shared_ptr<Embedding> embedding;
    int numNodeSamples;
    VecBuffer<1> buffer;
};
