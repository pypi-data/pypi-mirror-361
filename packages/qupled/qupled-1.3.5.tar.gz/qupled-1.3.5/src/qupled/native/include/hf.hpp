#ifndef HF_HPP
#define HF_HPP

#include "input.hpp"
#include "logger.hpp"
#include "numerics.hpp"
#include <vector>

// -----------------------------------------------------------------
// Solver for the Hartree-Fock scheme
// -----------------------------------------------------------------

class HF : public Logger {

public:

  // Constructor
  HF(const std::shared_ptr<const Input> &in_, const bool verbose_);
  explicit HF(const std::shared_ptr<const Input> &in_)
      : HF(in_, true) {}
  // Destructor
  virtual ~HF() = default;
  // Compute the scheme
  int compute();
  // Getters
  const Vector2D &getIdr() const { return idr; }
  const Vector2D &getLfc() const { return lfc; }
  const std::vector<double> &getSsf() const { return ssf; }
  const std::vector<double> &getWvg() const { return wvg; }
  std::vector<double> getRdf(const std::vector<double> &r) const;
  std::vector<double> getSdr() const;
  double getUInt() const;

protected:

  // Input data
  const std::shared_ptr<const Input> inPtr;
  // Integrator
  const std::shared_ptr<Integrator1D> itg;
  // Wave vector grid
  std::vector<double> wvg;
  // Ideal density response
  Vector2D idr;
  // Static local field correction
  Vector2D lfc;
  // Static structure factor
  std::vector<double> ssf;
  // Chemical potential
  double mu;
  // Access input pointer
  const Input &in() const { return *inPtr; }
  // Initialize basic properties
  virtual void init();
  // Calculations to compute the structural properties
  virtual void computeStructuralProperties();
  // Compute static structure factor
  virtual void computeSsf();
  virtual void computeSsfFinite();
  virtual void computeSsfGround();
  // Compute local field correction
  virtual void computeLfc();

private:

  // Construct wave vector grid
  void buildWaveVectorGrid();
  // Compute chemical potential
  void computeChemicalPotential();
  // Compute the ideal density response
  void computeIdr();
  void computeIdrFinite();
  void computeIdrGround();
};

namespace HFUtil {

  class Idr {

  public:

    // Constructor
    Idr(const int nl_,
        const double &x_,
        const double &Theta_,
        const double &mu_,
        const double &yMin_,
        const double &yMax_,
        std::shared_ptr<Integrator1D> itg_)
        : nl(nl_),
          x(x_),
          Theta(Theta_),
          mu(mu_),
          yMin(yMin_),
          yMax(yMax_),
          itg(itg_) {}
    // Get result of integration
    std::vector<double> get() const;

  private:

    // Number of matsubara frequency
    const int nl;
    // Wave-vector
    const double x;
    // Degeneracy parameter
    const double Theta;
    // Chemical potential
    const double mu;
    // Integration limits for finite temperature calculations
    const double yMin;
    const double yMax;
    // Idr integrand for frequency = l and wave-vector x
    double integrand(const double &y, const int &l) const;
    // Idr integrand for frequency = 0 and wave-vector x
    double integrand(const double &y) const;
    // Integrator object
    const std::shared_ptr<Integrator1D> itg;
  };

  class IdrGround {

  public:

    // Constructor
    IdrGround(const double &x_, const double &Omega_)
        : x(x_),
          Omega(Omega_) {}
    // Get
    double get() const;

  private:

    // Wave-vector
    const double x;
    // Frequency
    const double Omega;
  };

  class Ssf {

  public:

    // Constructor for finite temperature calculations
    Ssf(const double &x_,
        const double &Theta_,
        const double &mu_,
        const double &yMin_,
        const double &yMax_,
        std::shared_ptr<Integrator1D> itg_)
        : x(x_),
          Theta(Theta_),
          mu(mu_),
          yMin(yMin_),
          yMax(yMax_),
          itg(itg_) {}
    // Get at any temperature
    double get() const;

  private:

    // Wave-vector
    const double x;
    // Degeneracy parameter
    const double Theta;
    // Chemical potential
    const double mu;
    // Integration limits for finite temperature calculations
    const double yMin;
    const double yMax;
    // Integrator object
    const std::shared_ptr<Integrator1D> itg;
    // Get integrand
    double integrand(const double &y) const;
    // Get at zero temperature
    double get0() const;
  };

  class SsfGround {

  public:

    // Constructor for zero temperature calculations
    explicit SsfGround(const double &x_)
        : x(x_) {}
    // Get result
    double get() const;

  private:

    // Wave-vector
    const double x;
  };

} // namespace HFUtil

#endif
