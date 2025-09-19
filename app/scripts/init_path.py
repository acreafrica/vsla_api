def init_path():
    
    """ Solves module import error when running commmand line """

    import os, sys

    SCRIPTS_DIR = os.path.dirname( os.path.dirname(__file__) )

    print(SCRIPTS_DIR)

    PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)

    print(PROJECT_DIR)
    
    sys.path.append(PROJECT_DIR)
    #sys.path.append(SCRIPTS_DIR)


    return (PROJECT_DIR, SCRIPTS_DIR,)
