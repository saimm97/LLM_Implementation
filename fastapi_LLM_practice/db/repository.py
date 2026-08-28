def create_analysis(analysis_data,session) -> Analysis:

    new_analysis = Analysis(**analysis_data.model_dump()) 
    session.add(new_analysis)
    session.commit()
    session.refresh(new_analysis)
    return new_analysis