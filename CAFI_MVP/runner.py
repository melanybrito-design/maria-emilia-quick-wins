import time
from cafi_bot import NavigationError, SimulatedAdapter
from journal import worker_lock

def simulate(journal, run_id, *, synthetic_confirmed=False, scenario='success', limit=None, delay=0, adapter=None):
    if not synthetic_confirmed:
        raise ValueError('Confirme que el lote contiene exclusivamente datos sintéticos.')
    if limit is not None and (isinstance(limit,bool) or not isinstance(limit,int) or limit < 1):
        raise ValueError('El límite debe ser un entero positivo.')
    with worker_lock(journal.root):
        journal.recover()
        run = journal.get(run_id)
        if any(r['state'] in {'REQUIERE_REVISION','EN_PROCESO'} for r in run['rows']):
            raise ValueError('Hay intentos inciertos. Reanudación bloqueada; concilie antes de continuar.')
        if any(r['issues'] for r in run['rows']):
            raise ValueError('Corrija las incidencias del Excel y valide una nueva copia antes de simular.')
        journal.stop(run_id,False)
        journal.status(run_id,'EN_EJECUCION','Simulación en curso. No se está usando SIAC.')
        bot = adapter or SimulatedAdapter(scenario)
        attempted = 0
        current = None
        sent = False
        known_success = False
        exit_code = 0
        try:
            # Exportabilidad comprobada antes de iniciar la primera interacción.
            journal.export(run_id)
            for row in run['rows']:
                if row['state'] == 'PROCESADO':
                    continue
                if journal.metadata(run_id)['stop'] or (limit is not None and attempted >= limit):
                    exit_code = 3
                    break
                current, sent, known_success = row, False, False
                attempted += 1
                journal.transition(run_id,row['row'],'EN_PROCESO','PREPARACION','Intención de preparar el formulario simulado.')
                if delay:
                    time.sleep(delay)
                recipient = bot.prepare(row)
                if recipient != row['name']:
                    raise NavigationError('El destinatario no coincide.')
                journal.transition(run_id,row['row'],'VALIDADO','DESTINATARIO_SIMULADO','Destinatario verificado únicamente en simulador.')
                readback = bot.read_back(row)
                if readback != {k:row[k] for k in ['code','title','detail','priority']}:
                    raise NavigationError('La lectura de vuelta no coincide. No se guardó.')
                if journal.metadata(run_id)['stop']:
                    journal.transition(run_id,row['row'],'PENDIENTE','DETENCION','Detenido antes de guardar; no se envió.')
                    exit_code = 3
                    break
                journal.transition(run_id,row['row'],'EN_PROCESO','INTENCION_GUARDAR','Intención persistida antes del único guardado simulado.')
                sent = True
                outcome = bot.save()
                if outcome == 'rejected':
                    sent = False
                    journal.transition(run_id,row['row'],'ERROR','RECHAZO','Rechazo explícito simulado sin creación.')
                    exit_code = 2
                    break
                if outcome != 'success':
                    journal.transition(run_id,row['row'],'REQUIERE_REVISION','RESULTADO_INCIERTO','Resultado de guardado simulado incierto. No reintentar.')
                    exit_code = 3
                    break
                known_success = True
                journal.transition(run_id,row['row'],'PROCESADO','EXITO','Éxito observado en simulador; no es un trámite real.',f'SIM-{run_id[:6]}-{row["row"]}')
                journal.export(run_id)
                bot.acknowledge_and_reset()
                current = None
            status = 'COMPLETADO' if exit_code == 0 else 'DETENIDO'
            journal.status(run_id,status,'Simulación finalizada.' if exit_code == 0 else 'Lote detenido. Revise estados y bitácora antes de continuar.')
        except (Exception, KeyboardInterrupt) as exc:
            exit_code = 3
            if current:
                # Si la persistencia del éxito falló, EN_PROCESO se concilia al reiniciar.
                if not known_success:
                    state = 'REQUIERE_REVISION' if sent else 'ERROR'
                    journal.transition(run_id,current['row'],state,'DETENCION','Interrupción después de envío; conciliar.' if sent else 'Fallo antes del envío; no se guardó.')
            journal.status(run_id,'DETENIDO','Se detuvo por navegación, interrupción o escritura. Los éxitos registrados se conservan.')
            if not isinstance(exc,(NavigationError, OSError, KeyboardInterrupt)):
                raise
        finally:
            try:
                journal.export(run_id)
            except OSError:
                journal.status(run_id,'DETENIDO','No se pudo escribir resultados. Cierre Excel y vuelva a descargar; la bitácora conserva los estados.')
                exit_code = 3
        return exit_code
