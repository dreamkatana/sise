from app.extensions import db
from sqlalchemy import PrimaryKeyConstraint, ForeignKey, and_
from sqlalchemy.orm import foreign

class CursoAperf(db.Model):
    __tablename__ = 'V_EDUCORP_CURSO_APERF'
    CODCUA = db.Column(db.Integer, primary_key=True)
    NOMRED = db.Column(db.String(60))
    NOMCUA = db.Column(db.String(200))
    CODASS = db.Column(db.Integer)
    VALCUA = db.Column(db.Integer)
    TIPDUR = db.Column(db.Integer)
    TEMDUR = db.Column(db.Integer)
    CHRCUA = db.Column(db.BigInteger)
    FRECUA = db.Column(db.Float)
    MEDCUA = db.Column(db.Float)
    TURCUA = db.Column(db.String(1))
    DESCON = db.Column(db.Text)
    DESOBU = db.Column(db.Text)
    METCUA = db.Column(db.Text)
    PUBALV = db.Column(db.Text)
    CODFLT = db.Column(db.Integer)
    CODUSU = db.Column(db.BigInteger)
    PERRSV = db.Column(db.String(1))
    TIPREA = db.Column(db.Integer)
    TIPCER = db.Column(db.String(1))
    REGEXC = db.Column(db.Integer)
    REGSUB = db.Column(db.Integer)
    REGTRF = db.Column(db.Integer)
    NOMARQ = db.Column(db.String(250))
    TIPCUA = db.Column(db.String(1))
    EMICER = db.Column(db.String(1))
    CONWEB = db.Column(db.String(1))
    CODTST = db.Column(db.String(5))
    PRAAVA = db.Column(db.Integer)
    CONPDI = db.Column(db.String(1))
    CRIREP = db.Column(db.Integer)
    REGINC = db.Column(db.Integer)
    CONFRE = db.Column(db.Integer)
    REGCPL = db.Column(db.Integer)
    DATEXP = db.Column(db.DateTime)
    CONRES = db.Column(db.String(1))
    PRAARE = db.Column(db.Integer)
    CURTLT = db.Column(db.Integer)
    ABRLOC = db.Column(db.Text)
    AVATLT = db.Column(db.Integer)
    INIEFI = db.Column(db.Integer)
    TABORG = db.Column(db.Integer)
    METEFI = db.Column(db.Integer)
    DIAANT = db.Column(db.Integer)
    CURREC = db.Column(db.Integer)

class FichaCol(db.Model):
    __tablename__ = 'V_EDUCORP_FICHACOL'
    TIPCOL = db.Column(db.Integer, primary_key=True)
    NUMCAD = db.Column(db.Integer, primary_key=True)
    NOMFUN = db.Column(db.String(40))
    NUMCPF = db.Column(db.BigInteger)
    DATNAS = db.Column(db.DateTime)
    TIPSEX = db.Column(db.String(1))
    ESTADO_CIVIL = db.Column(db.String(13))
    TABORG = db.Column(db.Integer)
    NUMLOC = db.Column(db.Integer)
    ESTCAR = db.Column(db.Integer)
    CODCAR = db.Column(db.String(24))
    CODVIN = db.Column(db.Integer)
    DATADM = db.Column(db.DateTime)
    SITAFA = db.Column(db.Integer)
    DESSIT = db.Column(db.String(30))
    DESNAC = db.Column(db.String(40))
    NOMSOC = db.Column(db.String(70))
    NUMCID = db.Column(db.String(16))
    EMICID = db.Column(db.String(20))
    ESTCID = db.Column(db.String(2))
    DEXCID = db.Column(db.DateTime)
    TIPLGR = db.Column(db.String(5))
    ENDRUA = db.Column(db.String(80))
    ENDNUM = db.Column(db.String(6))
    ENDCPL = db.Column(db.String(25))
    ENDCEP = db.Column(db.Integer)
    DDDTEL = db.Column(db.Integer)
    NOMCID = db.Column(db.String(30))
    DESEST = db.Column(db.String(40))
    NOMPAI = db.Column(db.String(40))
    NUMTEL = db.Column(db.String(20))
    USU_DDDCEL = db.Column(db.Integer)
    USU_NUMCEL = db.Column(db.String(20))
    EMACOM = db.Column(db.String(100), unique=True, nullable=False)
    EMAPAR = db.Column(db.String(100))

    __table_args__ = (
        PrimaryKeyConstraint('TIPCOL', 'NUMCAD'),
    )

    cursos = db.relationship('CursoAperfCol',
                             primaryjoin="and_(FichaCol.TIPCOL==foreign(CursoAperfCol.TIPCOL), FichaCol.NUMCAD==foreign(CursoAperfCol.NUMCAD))",
                             back_populates='ficha_col')
    frequencia = db.relationship('FrequenciaTurma',
                                 primaryjoin="and_(FichaCol.TIPCOL==foreign(FrequenciaTurma.TIPCOL), FichaCol.NUMCAD==foreign(FrequenciaTurma.NUMCAD))",
                                 back_populates='ficha_col')

class CursoAperfCol(db.Model):
    __tablename__ = 'V_EDUCORP_CURSO_APERF_COL'
    TIPCOL = db.Column(db.Integer, primary_key=True)
    NUMCAD = db.Column(db.Integer, primary_key=True)
    CODCUA = db.Column(db.Integer, primary_key=True)
    SEQHCR = db.Column(db.Integer, primary_key=True)
    PERINI = db.Column(db.DateTime)
    PERFIM = db.Column(db.DateTime)
    CODOEM = db.Column(db.Integer)
    NOMOEM = db.Column(db.String(60))
    FRECUA = db.Column(db.Float)
    SITCUA = db.Column(db.Integer)
    DESSITCUA = db.Column(db.Text)
    TIPCER = db.Column(db.String(1))
    DESTIPCER = db.Column(db.Text)
    CARHOR = db.Column(db.BigInteger)
    DESFAS = db.Column(db.String(30))
    COMCUA = db.Column(db.String(250))
    TMACUA = db.Column(db.Integer)
    CERCUR = db.Column(db.LargeBinary)
    NOMCUA = db.Column(db.String(200))
    CERTSTRING = db.Column(db.Text)

    __table_args__ = (
        PrimaryKeyConstraint('TIPCOL', 'NUMCAD', 'CODCUA', 'SEQHCR'),  
    )

    curso_aperf = db.relationship('CursoAperf', 
                                  primaryjoin="foreign(CursoAperfCol.CODCUA)==CursoAperf.CODCUA",
                                  backref=db.backref('colaboradores', lazy=True))
    ficha_col = db.relationship('FichaCol',
                                primaryjoin="and_(foreign(CursoAperfCol.TIPCOL)==FichaCol.TIPCOL, foreign(CursoAperfCol.NUMCAD)==FichaCol.NUMCAD)",
                                back_populates='cursos')

class FrequenciaTurma(db.Model):
    __tablename__ = 'V_EDUCORP_FREQUENCIA_TURMA'
    CODCUA = db.Column(db.Integer, primary_key=True)
    TMACUA = db.Column(db.Integer, primary_key=True)
    NUMEMP = db.Column(db.Integer, primary_key=True)
    TIPCOL = db.Column(db.Integer, primary_key=True)
    NUMCAD = db.Column(db.Integer, primary_key=True)
    QTDFAL = db.Column(db.Integer)
    SITCUA = db.Column(db.Integer)
    HORFAL = db.Column(db.BigInteger)

    __table_args__ = (
        PrimaryKeyConstraint('CODCUA', 'TMACUA', 'NUMEMP', 'TIPCOL', 'NUMCAD'),
    )

    ficha_col = db.relationship('FichaCol',
                                primaryjoin="and_(foreign(FrequenciaTurma.TIPCOL)==FichaCol.TIPCOL, foreign(FrequenciaTurma.NUMCAD)==FichaCol.NUMCAD)",
                                back_populates='frequencia')
