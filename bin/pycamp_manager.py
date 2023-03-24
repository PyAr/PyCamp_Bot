import argparse
import datetime
import logging
from pycamp_bot.models import Pycamp
from pycamp_bot.models import Pycampista
from pycamp_bot.models import PycampistaAtPycamp
from pycamp_bot.models import models_db_connection


def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='wich')

    parser.add_argument('--list_pycampistas', action='store_true',
                        help='List all pycampistas in the DB.')
    parser.add_argument('--list_pycamps', action='store_true',
                        help='List all pycamps in the DB.')

    pycampista_parser = subparsers.add_parser('pycampista', help='Manage Pycampista.')
    pycampista_parser.add_argument('name', help='Pycampista.')
    pycampista_parser.add_argument('--add', action='store_true', help='Add pycampista.')
    pycampista_parser.add_argument('--arrive',
                                   nargs='?',
                                   const=datetime.datetime.now().isoformat(),
                                   help='Add arrival time as isoformat\
                                   datetime. Example:\
                                   2020-03-11T09:40:37.577157, 2020-03-11')
    pycampista_parser.add_argument('--departure',
                                   nargs='?',
                                   const=datetime.datetime.now().isoformat(),
                                   help='Add departure time as isoformat\
                                   datetime. Example:\
                                   2020-03-11T09:40:37.577157, 2020-03-11')

    pycamp_parser = subparsers.add_parser('pycamp', help='Manage Pycamp.')
    pycamp_parser.add_argument('name', help='Pycamp headquarters name.')
    pycamp_parser.add_argument('--add', action='store_true', help='Add Pycamp.')
    pycamp_parser.add_argument('--add_pycampista',
                               help='Add Pycampista to pycamp.')
    pycamp_parser.add_argument('--init',
                               nargs='?',
                               const=datetime.datetime.now().isoformat(),
                               help='Add pycamps init time as isoformat\
                               datetime. Example:\
                               2020-03-11T09:40:37.577157, 2020-03-11')
    pycamp_parser.add_argument('--end',
                               nargs='?',
                               const=datetime.datetime.now().isoformat(),
                               help='Add pycamp end time as isoformat\
                               datetime. Example:\
                               2020-03-11T09:40:37.577157, 2020-03-11')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    models_db_connection()

    if args.wich == 'pycampista':
        if args.add:
            logging.info('Adding pycampista')
            pycampista = Pycampista.create(username=args.name)

        if args.arrive:
            arrive_time = datetime.datetime.fromisoformat(args.arrive)
            logging.info('Changing arrive time to {}'.format(arrive_time))
            pycampista = Pycampista.select().where(
                Pycampista.username == args.name)[0]
            pycampista.arrive = arrive_time
            pycampista.save()

        if args.departure:
            departure_time = datetime.datetime.fromisoformat(args.departure)
            logging.info('Changing departure time to {}'.format(departure_time))
            pycampista = Pycampista.select().where(
                Pycampista.username == args.name)[0]
            pycampista.leave = departure_time
            pycampista.save()

        pycampista = Pycampista.select().where(
            Pycampista.username == args.name)[0]
        print(pycampista)
    elif args.wich == 'pycamp':
        if args.add:
            logging.info('Adding pycamp')
            pycamp = Pycamp.create(headquarters=args.name)

        if args.init:
            init_time = datetime.datetime.fromisoformat(args.init)
            logging.info('Changing init time to {}'.format(init_time))
            pycamp = Pycamp.select().where(
                Pycamp.headquarters == args.name)[0]
            pycamp.init = init_time
            pycamp.save()

        if args.end:
            end_time = datetime.datetime.fromisoformat(args.end)
            logging.info('Changing end time to {}'.format(end_time))
            pycamp = Pycamp.select().where(
                Pycamp.headquarters == args.name)[0]
            pycamp.end = end_time
            pycamp.save()

        if args.add_pycampista:
            pycamp = Pycamp.select().where(
                Pycamp.headquarters == args.name)[0]
            pycampista = Pycampista.select().where(
                Pycampista.username == args.add_pycampista)[0]
            pycampista_at_pycamp = PycampistaAtPycamp.create(pycamp=pycamp,
                                                             pycampista=pycampista)

        pycamp = Pycamp.select().where(
            Pycamp.headquarters == args.name)[0]
        print(pycamp)
        pycampistas_at_pycamp = PycampistaAtPycamp.select().where(
            PycampistaAtPycamp.pycamp == pycamp)
        for pap in pycampistas_at_pycamp:
            print('-' * 10)
            print(pap.pycampista)
    elif args.list_pycamps:
        pycamps = Pycamp.select()
        for pycamp in pycamps:
            print('-' * 10)
            print(pycamp)
    elif args.list_pycampistas:
        pycampistas = Pycampista.select()
        for pycampista in pycampistas:
            print('-' * 10)
            print(pycampista)
