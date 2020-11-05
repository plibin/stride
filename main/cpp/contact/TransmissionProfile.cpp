/*
 *  This is free software: you can redistribute it and/or modify it
 *  under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  any later version.
 *  The software is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *  You should have received a copy of the GNU General Public License
 *  along with the software. If not, see <http://www.gnu.org/licenses/>.
 *
 *  Copyright 2019, Kuylen E, Willem L, Broeckhove J
 */

/**
 * @file
 * Implementation for the TransmissionProfile class.
 */

#include "TransmissionProfile.h"

#include <cmath>
#include <boost/math/distributions/gamma.hpp>


namespace stride {

using namespace std;
using namespace boost::property_tree;

void TransmissionProfile::Initialize(const ptree& configPt, const ptree& diseasePt, util::RnMan& rnMan)
{
		// Check wether to use r0 or transmission probability
		boost::optional<double> transmissionProbabilityAsInput = configPt.get_optional<double>("run.transmission_probability");

		if (transmissionProbabilityAsInput) {

			// Use transmission probability as input parameter
			m_transmission_probability = *transmissionProbabilityAsInput;

		} else {
			// Use R0 as input parameter
			// parse config file
				const auto r0 = configPt.get<double>("run.r0");
				const auto b0 = diseasePt.get<double>("disease.transmission.b0");
				const auto b1 = diseasePt.get<double>("disease.transmission.b1");
				const auto b2 = diseasePt.get<double>("disease.transmission.b2");

				// if linear model is fitted to simulation data:
				if(b2 == 0){
				    	// Expected(R0) = (b0 + b1*transm_prob).
				    	m_transmission_probability = (r0 - b0) / b1;

				} else{
					// if quadratic model is fitted to simulation data:
				    	// Expected(R0) = (b0 + b1*transm_prob + b2*transm_prob^2).
				    	// Find root
					const auto a = b2;
					const auto b = b1;
					const auto c = b0 - r0;

					// To obtain a real values (instead of complex)
					if (r0 < (-(b * b) / (4 * a))) {
						const double determ = (b * b) - 4 * a * c;
						m_transmission_probability = (-b + sqrt(determ)) / (2 * a);
					} else {
						throw runtime_error("TransmissionProfile::Initialize> Illegal input values.");
					}
				}
		}

		// Check whether transmission probability follows a distribution or is constant
		boost::optional<string> tProbDistribution = configPt.get_optional<string>("run.transmission_probability_distribution");
		if (tProbDistribution) {
			m_transmission_probability_distribution = *tProbDistribution;
			// Get target overdispersion
			m_transmission_probability_distribution_overdispersion = configPt.get<double>("run.transmission_probability_distribution_overdispersion", 0);
		}

		m_rn_man_p = std::make_unique<util::RnMan>(rnMan);

}

double TransmissionProfile::DrawIndividualProbability() const
{
	if (m_transmission_probability_distribution == "Constant") {
		return m_transmission_probability;
	} else if (m_transmission_probability_distribution == "Gamma") {
		// Generate truncated (between 0 and 1) gamma distribution
		// Based on script https://rdrr.io/cran/RGeode/src/R/rgammatr.R
		double shape = m_transmission_probability_distribution_overdispersion;
		double scale = m_transmission_probability / shape;

		boost::math::gamma_distribution gamma_dist = boost::math::gamma_distribution<double>(shape, scale);

		double cdf1 = cdf(gamma_dist, 0.0);
		double cdf2 = cdf(gamma_dist, 1.0);

		auto generator = m_rn_man_p->GetUniform01Generator();
		double individual_probability = quantile(gamma_dist, cdf1 + generator() * (cdf2 - cdf1));

		return individual_probability;

	} else {
		return m_transmission_probability;
	}
}

} // namespace stride
