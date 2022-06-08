% Pololu robot emulation TCP/IP %
% Rafal Osypiuk %

clear all;

% TCP/IP server definition on localhost port no: 8000
t = tcpip('127.0.0.1', 8000, 'NetworkRole', 'server');
disp('Waiting for connection');
% open socket
fopen(t);
disp('Connection OK!');
% define termination character
t.Terminator = ']';

ii=1; data_count=1000;
while ii <= data_count
    
    data = fscanf(t)
    pause(0.1);
    fprintf(t, '[01c012D000F401E803DC05c0f7]');
    
    ii=ii+1;
end

fclose(t);
disp('End of emulation.');
