from sqlalchemy import (
    Column, Integer, String, Date, Float, ForeignKey, JSON
)
from sqlalchemy.orm import relationship, declarative_base
 

Base = declarative_base()
 
#########################
#### Document tables ####
#########################
class Document(Base):
    # Documents represent the actual documents which info was extracted into our database
    # the 'document_path' field represents where to find the document in the S3 bucket
    __tablename__ = 'documents'
    document_id = Column(Integer, primary_key=True, autoincrement=True)
    document_name = Column(String, unique=True)
    document_path = Column(String, unique=True)
    source_id = Column(Integer, ForeignKey('sources.source_id'))
    start_date_effect = Column(Date)
    end_date_effect = Column(Date)
    date_publication = Column(Date)
    date_ingestion = Column(Date)
