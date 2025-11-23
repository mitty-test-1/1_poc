from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, ForeignKey, UUID, JSON, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), default='user')
    preferences = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    # Relationships
    conversations = relationship("Conversation", back_populates="user")
    messages = relationship("Message", back_populates="sender")
    user_profiles = relationship("UserProfile", back_populates="user", uselist=False)
    admin_logs = relationship("AdminLog", back_populates="admin")
    personalization_data = relationship("PersonalizationData", back_populates="user")
    analytics_data = relationship("AnalyticsData", back_populates="user")

class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    admin_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    title = Column(String(255))
    metadata = Column(JSONB, default=dict)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    status = Column(String(50), default='active')

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="conversations")
    admin = relationship("User", foreign_keys=[admin_id])
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = 'messages'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey('conversations.id'), nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    attachments = Column(JSONB, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    message_type = Column(String(50), default='text')

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", back_populates="messages")

class UserProfile(Base):
    __tablename__ = 'user_profiles'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    preferences = Column(JSONB, default=dict)
    demographics = Column(JSONB, default=dict)
    settings = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="user_profiles")

class AdminLog(Base):
    __tablename__ = 'admin_logs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    action = Column(String(100), nullable=False)
    target_table = Column(String(100), nullable=False)
    target_id = Column(UUID(as_uuid=True), nullable=False)
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    admin = relationship("User", back_populates="admin_logs")

class PersonalizationData(Base):
    __tablename__ = 'personalization_data'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    behavior_type = Column(String(100), nullable=False)
    data_value = Column(JSONB, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="personalization_data")

class AIModel(Base):
    __tablename__ = 'ai_models'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    status = Column(String(50), default='available')
    performance_metrics = Column(JSONB, default=dict)
    config = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

class AnalyticsData(Base):
    __tablename__ = 'analytics_data'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    metric_type = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSONB, default=dict)

    # Relationships
    user = relationship("User", back_populates="analytics_data")

# Indexes for performance optimization
Index('idx_user_profiles_user_id', UserProfile.user_id)
Index('idx_admin_logs_admin_id', AdminLog.admin_id)
Index('idx_admin_logs_timestamp', AdminLog.timestamp)
Index('idx_personalization_data_user_id', PersonalizationData.user_id)
Index('idx_personalization_data_timestamp', PersonalizationData.timestamp)
Index('idx_ai_models_name_version', AIModel.model_name, AIModel.version)
Index('idx_analytics_data_user_id', AnalyticsData.user_id)
Index('idx_analytics_data_metric_type', AnalyticsData.metric_type)
Index('idx_analytics_data_timestamp', AnalyticsData.timestamp)

# Database connection setup
def get_engine(database_url: str = None):
    """Get SQLAlchemy engine"""
    if database_url is None:
        database_url = 'postgresql://postgres:password@localhost:5432/chatbot'

    return create_engine(
        database_url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True
    )

def get_session_local(engine=None):
    """Get session factory"""
    if engine is None:
        engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables(engine=None):
    """Create all tables"""
    if engine is None:
        engine = get_engine()
    Base.metadata.create_all(bind=engine)

def drop_tables(engine=None):
    """Drop all tables"""
    if engine is None:
        engine = get_engine()
    Base.metadata.drop_all(bind=engine)