// Full-alphabet frozen reporting for the external KenLM baseline, not FP Runtime.
#include <lm/model.hh>
#include <lm/state.hh>
#include <lm/enumerate_vocab.hh>

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

namespace {
std::uint64_t number(const char *text) {
  std::string value(text);
  if (value.empty() || value.find_first_not_of("0123456789") != std::string::npos)
    throw std::runtime_error("unsigned decimal argument required");
  return std::stoull(value);
}

struct Sum {
  double value = 0, correction = 0;
  void add(double x) {
    double adjusted = x - correction;
    double next = value + adjusted;
    correction = (next - value) - adjusted;
    value = next;
  }
};

struct Vocabulary : lm::EnumerateVocab {
  const lm::WordIndex missing = std::numeric_limits<lm::WordIndex>::max();
  std::vector<lm::WordIndex> real;
  lm::WordIndex unk, bos, eos;
  std::size_t entries = 0;
  explicit Vocabulary(std::size_t size) : real(size, missing), unk(missing), bos(missing), eos(missing) {}
  void Add(lm::WordIndex ordinal, const StringPiece &piece) override {
    if (ordinal != entries++) throw std::runtime_error("incomplete vocabulary enumeration");
    const std::string word(piece.data(), piece.size());
    if (word == "<unk>") { unk = ordinal; return; }
    if (word == "<s>") { bos = ordinal; return; }
    if (word == "</s>") { eos = ordinal; return; }
    if (word.empty() || word[0] != 't') throw std::runtime_error("model contains a foreign token spelling");
    const auto token = number(word.c_str()+1);
    if (token >= real.size() || word != "t" + std::to_string(token) || real[token] != missing)
      throw std::runtime_error("model vocabulary is not an injective declared token-ID map");
    real[token] = ordinal;
  }
};

int run(int argc, char **argv) {
  if (argc != 6 && argc != 7)
    throw std::runtime_error("usage: fp_kenlm_report MODEL DATA_UINT16_LE V COUNT CONTEXT_CAP [--rows]");
  const auto vocabulary = number(argv[3]), count = number(argv[4]), context = number(argv[5]);
  const bool rows = argc == 7 && std::string(argv[6]) == "--rows";
  if (!vocabulary || vocabulary > 65536 || !count || context > 65536 ||
      (argc == 7 && !rows) || (rows && (vocabulary > 128 || count > 32)))
    throw std::runtime_error("invalid dimensions or oversized diagnostic rows");
  std::ifstream input(argv[2], std::ios::binary);
  if (!input) throw std::runtime_error("cannot open registered token file");
  input.seekg(0, std::ios::end);
  const auto bytes = input.tellg();
  if (bytes < 0 || count > std::uint64_t(bytes) / 2 || std::uint64_t(bytes) % 2)
    throw std::runtime_error("token view exceeds a complete uint16 file");
  input.seekg(0);

  Vocabulary vocabulary_map(vocabulary);
  lm::ngram::Config config;
  config.enumerate_vocab = &vocabulary_map;
  lm::ngram::TrieModel model(argv[1], config);
  if (vocabulary_map.unk != model.GetVocabulary().NotFound() ||
      vocabulary_map.bos != model.GetVocabulary().BeginSentence() ||
      vocabulary_map.eos != model.GetVocabulary().EndSentence())
    throw std::runtime_error("complete model vocabulary and structural markers required");
  if (model.Order() - 1 > context)
    throw std::runtime_error("ngram history exceeds the declared context cap");
  std::vector<lm::WordIndex> words;
  std::vector<std::size_t> column(vocabulary);
  std::vector<bool> unknown(vocabulary);
  std::unordered_map<lm::WordIndex, std::size_t> unique;
  std::size_t unseen = 0;
  for (std::size_t token = 0; token < vocabulary; ++token) {
    unknown[token] = vocabulary_map.real[token] == vocabulary_map.missing;
    const auto word = unknown[token] ? vocabulary_map.unk : vocabulary_map.real[token];
    unseen += unknown[token];
    auto found = unique.find(word);
    if (found == unique.end()) {
      const auto ordinal = words.size();
      unique.emplace(word, ordinal);
      words.push_back(word);
      column[token] = ordinal;
    } else {
      // Only genuinely unseen IDs may share the model's <unk> bucket.
      if (!unknown[token]) throw std::runtime_error("distinct real IDs alias a known vocabulary word");
      column[token] = found->second;
    }
  }
  lm::ngram::State state = model.BeginSentenceState(), scratch, next;
  const double ln10 = std::log(10.0), log_unseen = unseen ? std::log(double(unseen)) : 0;
  std::vector<float> scores(words.size());
  Sum total_loss;
  std::cout << std::setprecision(17);
  if (rows) std::cout << "{\"rows\":[";
  for (std::uint64_t t = 0; t < count; ++t) {
    // Form the complete distribution before looking up this event's target.
    double largest = -std::numeric_limits<double>::infinity();
    for (std::size_t i = 0; i < words.size(); ++i) {
      scores[i] = model.FullScore(state, words[i], scratch).prob;
      if (!std::isfinite(scores[i])) throw std::runtime_error("nonfinite model score");
      largest = std::max(largest, double(scores[i]));
    }
    Sum scaled;
    for (auto score : scores) scaled.add(std::exp((double(score) - largest) * ln10));
    const double log_total = largest * ln10 + std::log(scaled.value);
    unsigned char raw[2];
    input.read(reinterpret_cast<char *>(raw), 2);
    if (!input) throw std::runtime_error("short token read");
    const auto target = std::uint32_t(raw[0]) | (std::uint32_t(raw[1]) << 8);
    if (target >= vocabulary) throw std::runtime_error("target outside the declared alphabet");
    const double loss = log_total - double(scores[column[target]]) * ln10 + (unknown[target] ? log_unseen : 0);
    if (!std::isfinite(loss) || loss < -1e-12) throw std::runtime_error("invalid normalized log loss");
    total_loss.add(loss);
    if (rows) {
      if (t) std::cout << ',';
      std::cout << "{\"position\":" << t << ",\"target\":" << target << ",\"nll\":" << loss << ",\"probabilities\":[";
      for (std::size_t token = 0; token < vocabulary; ++token) {
        if (token) std::cout << ',';
        const double logp = double(scores[column[token]]) * ln10 - log_total - (unknown[token] ? log_unseen : 0);
        std::cout << std::exp(logp);
      }
      std::cout << "]}";
    }
    const auto observed = model.FullScore(state, words[column[target]], next).prob;
    if (observed != scores[column[target]]) throw std::runtime_error("pre-target distribution changed");
    state = next;
  }
  if (rows) std::cout << "],\"summary\":";
  std::cout << "{\"status\":\"COMPLETE_FROZEN_KENLM_REPORT\",\"tokens\":" << count
            << ",\"mean_nll_nats\":" << total_loss.value / double(count)
            << ",\"vocabulary\":" << vocabulary << ",\"order\":" << unsigned(model.Order())
            << ",\"context_cap\":" << context << ",\"seen_real_ids\":" << vocabulary-unseen
            << ",\"unseen_real_ids\":" << unseen << ",\"scored_model_columns\":" << words.size()
            << ",\"normalization\":\"all real labels; one UNK bucket split uniformly; no EOS target\"}";
  if (rows) std::cout << '}';
  std::cout << '\n';
  return 0;
}
} // namespace

int main(int argc, char **argv) {
  try {
    return run(argc, argv);
  } catch (const std::exception &error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
