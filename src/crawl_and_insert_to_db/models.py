from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

Base = declarative_base()

class PDChuDe(Base):
    __tablename__ = "pd_chude"
    id = Column(String(128), primary_key=True)
    ten = Column(Text)
    stt = Column(Integer)

    demuc = relationship("PDDeMuc", backref="pd_chude", lazy=True)
    dieu = relationship("PDDieu", backref="pd_chude", lazy=True)


class PDDeMuc(Base):
    __tablename__ = "pd_demuc"
    id = Column(String(128), primary_key=True)
    ten = Column(Text)
    stt = Column(Integer)
    chude_id = Column(String(128), ForeignKey('pd_chude.id'))

    chuong = relationship("PDChuong", backref="pd_demuc", lazy=True)
    dieu = relationship("PDDieu", backref="pd_demuc", lazy=True)


class PDChuong(Base):
    __tablename__ = "pd_chuong"
    mapc = Column(String(128), primary_key=True)
    ten = Column(Text)
    demuc_id = Column(String(128), ForeignKey("pd_demuc.id"))
    chimuc = Column(Text)
    stt = Column(Integer)

    dieu = relationship("PDDieu", backref="pd_chuong", lazy=True)


class PDDieu(Base):
    __tablename__ = "pd_dieu"
    mapc = Column(String(128), primary_key=True)
    ten = Column(Text)
    noidung = Column(Text)
    chimuc = Column(Integer)
    vbqppl = Column(Text)
    vbqppl_link = Column(Text)
    stt = Column(Integer)
    demuc_id = Column(String(128), ForeignKey("pd_demuc.id"))
    chuong_id = Column(String(128), ForeignKey("pd_chuong.mapc"))
    chude_id = Column(String(128), ForeignKey("pd_chude.id"))

    table = relationship("PDTable", backref="pd_dieu", lazy=True)
    file = relationship("PDFile", backref="pd_dieu", lazy=True)


class PDTable(Base):
    __tablename__ = "pd_table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    dieu_id = Column(String(128), ForeignKey("pd_dieu.mapc"))
    html = Column(Text)


class PDFile(Base):
    __tablename__ = "pd_file"
    id = Column(Integer, primary_key=True, autoincrement=True)
    dieu_id = Column(String(128), ForeignKey("pd_dieu.mapc"))
    link = Column(Text)
    path = Column(Text)


class PDMucLienQuan(Base):
    __tablename__ = "pd_muclienquan"
    dieu_id = Column(String(128), ForeignKey("pd_dieu.mapc"))
    dieu_id_lienquan = Column(String(128), ForeignKey("pd_dieu.mapc"))

    __table_args__ = (
        PrimaryKeyConstraint("dieu_id", "dieu_id_lienquan"),
    )

PDDieu.muclienquan = relationship(
    "PDDieu",
    secondary=PDMucLienQuan.__table__,
    primaryjoin=PDDieu.mapc == PDMucLienQuan.dieu_id,
    secondaryjoin=PDDieu.mapc == PDMucLienQuan.dieu_id_lienquan,
    backref="related_dieu",
    lazy=True
)