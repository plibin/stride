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
 *  Copyright 2019, Willem L, Kuylen E, Broeckhove J
 */

/**
 * @file
 * Header for the TransmissionProfile class.
 */

#pragma once

#include "util/RnMan.h"

#include <boost/property_tree/ptree.hpp>

namespace stride {

/**
 * Transmission probability from disease data.
 */
class TransmissionProfile
{
public:
        TransmissionProfile() : m_transmission_probability(0.0), m_transmission_probability_distribution("Constant"),
								m_transmission_probability_distribution_overdispersion(0), m_rn_man_p() {}

        /// Return transmission probability.
        double GetProbability() const { return m_transmission_probability; }

        /// Return individual transmission probability.
        double DrawIndividualProbability() const;

        /// Initialize.
        void Initialize(const boost::property_tree::ptree& configPt, const boost::property_tree::ptree& diseasePt, util::RnMan& rnMan);

private:
        double m_transmission_probability;
        std::string m_transmission_probability_distribution;
        double m_transmission_probability_distribution_overdispersion;

        std::unique_ptr<util::RnMan> m_rn_man_p;	// FIXME is this ok cfr. splitting of random number stream?
};

} // namespace stride
