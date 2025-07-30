/*-=-=-=-=-=-=-=-=-=-=-=-=-=-= Section Includes -=-=-=-=-=-=-=-=-=-=-=-=-=-=*/
#include "gomea/src/fitness/benchmarks-discrete.hpp"
/*-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=*/
namespace gomea{
namespace fitness{

hierarchicalDeceptiveTrapBBO_t::hierarchicalDeceptiveTrapBBO_t( int number_of_variables, int trap_size ) : BBOFitnessFunction_t<char>(number_of_variables)
{
	if(trap_size < 3)
		throw std::runtime_error("Hierarchical deceptive trap function requires a trap size of at least 3.");
	int symbols = number_of_variables;
	while( symbols > 1 )
	{
		if( symbols % trap_size != 0 )
			throw std::runtime_error("Number of variables at each level must be a multiple of trap_size for hierarchical deceptive trap function.");
		symbols /= trap_size;
	}
	this->name = "Hierarchical deceptive trap function";
	this->trap_size = trap_size;
	this->vtr = computeVTR();
	this->use_vtr = true;
	this->initialize();
}

double hierarchicalDeceptiveTrapBBO_t::objectiveFunction( int objective_index, vec_t<char> &variables )
{
	int number_of_symbols = number_of_variables;
	char *symbols = new char[number_of_symbols];
	for( int i = 0; i < number_of_variables; i++ )
		symbols[i] = (variables[i] == 1) ? '1' : '0';

	double result           = 0;
	double level_multiplier = (double) trap_size;
	while( number_of_symbols >= trap_size )
	{
		double level_result = 0;
		for( int i = 0; i < number_of_symbols / trap_size; i++ )
		{
			int unitation = 0;
			for( int j = i*trap_size; j < (i+1)*trap_size; j++ )
			{
				if( symbols[j] == '1' )
					unitation++;
				if( symbols[j] == '-' )	{
					unitation = -1;
					break;
				}
			}
			if( unitation >= 0 )
			{
				if( number_of_symbols > trap_size )
				{
					if(unitation == trap_size)
						level_result += 1;
					else
						level_result += ((double) (trap_size - unitation - 1))/((double) (trap_size - 1));
				}
				else
				{
					if(unitation == trap_size)
						level_result += 1;
					else
						level_result += 0.9 * ((double) (trap_size - unitation - 1))/((double) (trap_size - 1));
				}
			}
		}
		result            += level_result*level_multiplier;
		level_multiplier  *= trap_size;

		for( int i = 0; i < number_of_symbols / trap_size; i++ )
		{
			int unitation = 0;
			for( int j = i*trap_size; j < (i+1)*trap_size; j++ )
			{
				if( symbols[j] == '1' )
					unitation++;
				if( symbols[j] == '-' )
				{
					unitation = -1;
					break;
				}
			}
			symbols[i] = '-';
			if( unitation == trap_size )
				symbols[i] = '1';
			if( unitation == 0 )
				symbols[i] = '0';
		}
		number_of_symbols /= trap_size;
	}
	delete[] symbols;
	return result;
}

double hierarchicalDeceptiveTrapBBO_t::computeVTR()
{
	int logl = 0;
	int symbols = number_of_variables;
	while( symbols > 1 ){
		logl++;
		symbols /= trap_size;
	}
	return logl*number_of_variables;
}

double hierarchicalDeceptiveTrapBBO_t::getSimilarityMeasure( size_t var_a, size_t var_b )
{
	if( var_a == var_b )
		return 1.0;
	else{
		double result = 1.0;
		int k = trap_size;
		while( k < number_of_variables )
		{
			if(var_a / k == var_b / k)
				result *= trap_size;
			k *= trap_size;
		}
		return result;
	}
}

}}
/*-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=*/
