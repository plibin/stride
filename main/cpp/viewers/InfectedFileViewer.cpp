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
 *  Copyright 2018, Kuylen E, Willem L, Broeckhove J
 */

/**
 * @file
 * Definition of Observer for Infected output.
 */

#include "InfectedFileViewer.h"

#include "pop/Population.h"
#include "sim/Sim.h"
#include "sim/SimRunner.h"

using namespace std;
using namespace stride::sim_event;

namespace stride {
namespace viewers {

InfectedFileViewer::InfectedFileViewer(std::shared_ptr<SimRunner> runner, const std::string& output_prefix)
            : m_output_prefix(output_prefix), m_infected(), m_infected_base(), m_infected_uk(), m_exposed(), m_infectious(), m_symptomatic(), m_infected_total(),
			  m_runner(std::move(runner))
        {
        }



void InfectedFileViewer::Update(const sim_event::Id id)
{
        switch (id) {
        case Id::AtStart:
        case Id::Stepped: {
                const auto pop = m_runner->GetSim()->GetPopulation();
                m_infected.push_back(pop->CountInfectedCases());
                m_infected_base.push_back(pop->CountInfectedCasesPerVariant("base"));
                m_infected_uk.push_back(pop->CountInfectedCasesPerVariant("uk"));
                m_exposed.push_back(pop->CountExposedCases());
                m_infectious.push_back(pop->CountInfectiousCases());
                m_symptomatic.push_back(pop->CountSymptomaticCases());
                m_infected_total.push_back(pop->GetTotalInfected());
                break;
        }
        case Id::Finished: {
        		output::InfectedFile infected_file(m_output_prefix, "infected");
        		infected_file.Print(m_infected);
        		
                output::InfectedFile infected_file_base(m_output_prefix, "infected_base");
        		infected_file_base.Print(m_infected_base);
                
                output::InfectedFile infected_file_uk(m_output_prefix, "infected_uk");
        		infected_file_uk.Print(m_infected_uk);

        		output::InfectedFile exposed_file(m_output_prefix, "exposed");
        		exposed_file.Print(m_exposed);

        		output::InfectedFile infectious_file(m_output_prefix, "infectious");
        		infectious_file.Print(m_infectious);

        		output::InfectedFile symptomatic_file(m_output_prefix, "symptomatic");
        		symptomatic_file.Print(m_symptomatic);

        		output::InfectedFile infected_total_file(m_output_prefix, "cases");
        		infected_total_file.Print(m_infected_total);
                break;
        }
        default: break;
        }
}

} // namespace viewers
} // namespace stride
